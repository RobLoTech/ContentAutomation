import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

class AffiliateEnricher:
    def __init__(self):
        self.partners = self.load_affiliate_config()
    
    def load_affiliate_config(self):
        """Load affiliate partner configuration"""
        return {
            'amazon': {
                'tag': os.getenv('AMAZON_ASSOCIATE_TAG', 'roblotech-20'),
                'keywords': ['book', 'device', 'hardware', 'gadget', 'equipment', 'tool', 'yubikey', 'router', 'hard drive'],
                'base_url': 'https://www.amazon.com/s?tag={tag}&k={query}'
            },
            'stacksocial': {
                'id': os.getenv('STACKSOCIAL_AFFILIATE_ID', ''),
                'keywords': ['software', 'productivity', 'app', 'course', 'training', 'bundle', 'deal'],
                'base_url': 'https://stacksocial.com/?rid={id}'
            },
            'appsumo': {
                'id': os.getenv('APPSUMO_AFFILIATE_ID', ''),
                'keywords': ['saas', 'startup', 'business tool', 'ai tool', 'automation', 'lifetime deal'],
                'base_url': 'https://appsumo.com/?rf={id}'
            },
            'cyberghost': {
                'id': os.getenv('CYBERGHOST_AFFILIATE_ID', ''),
                'keywords': ['vpn', 'cyberghost', 'privacy', 'encryption', 'anonymity', 'virtual private network'],
                'base_url': 'https://www.cyberghostvpn.com/?aid={id}'
            },
            'namecheap': {
                'id': os.getenv('NAMECHEAP_AFFILIATE_ID', ''),
                'keywords': ['domain', 'hosting', 'ssl', 'website', 'registrar', 'dns'],
                'base_url': 'https://www.namecheap.com/?aff={id}'
            },
            'grammarly': {
                'id': os.getenv('GRAMMARLY_AFFILIATE_ID', ''),
                'keywords': ['writing', 'grammar', 'ai writing', 'content creation', 'proofreading'],
                'base_url': 'https://www.grammarly.com/?affiliateID={id}'
            }
        }
    
    def detect_keywords(self, text, partner_keywords):
        """Detect if text contains partner keywords"""
        text_lower = text.lower()
        for keyword in partner_keywords:
            if keyword.lower() in text_lower:
                return keyword
        return None
    
    def create_affiliate_link(self, partner_name, keyword):
        """Create affiliate link for partner"""
        partner = self.partners.get(partner_name)
        
        if not partner:
            return None
        
        partner_id = partner.get('id') or partner.get('tag')
        if not partner_id:
            return None
        
        base_url = partner['base_url']
        
        if '{tag}' in base_url:
            return base_url.format(tag=partner_id, query=keyword.replace(' ', '+'))
        elif '{id}' in base_url:
            return base_url.format(id=partner_id)
        
        return None
    
    def enrich_html_content(self, html_content):
        """Enrich HTML content with affiliate links"""
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text()
        
        enrichments = []
        
        for partner_name, partner_config in self.partners.items():
            keyword = self.detect_keywords(text_content, partner_config['keywords'])
            
            if keyword:
                affiliate_link = self.create_affiliate_link(partner_name, keyword)
                
                if affiliate_link:
                    enrichments.append({
                        'partner': partner_name,
                        'keyword': keyword,
                        'link': affiliate_link
                    })
        
        return enrichments
    
    def wrap_keywords_with_links(self, html_content, enrichments, max_replacements=3):
        """Wrap keywords with affiliate links in HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for enrichment in enrichments[:max_replacements]:
            keyword = enrichment['keyword']
            link = enrichment['link']
            partner = enrichment['partner']
            
            for text_node in soup.find_all(string=re.compile(re.escape(keyword), re.IGNORECASE)):
                if text_node.parent.name == 'a':
                    continue
                
                pattern = re.compile(f'\\b{re.escape(keyword)}\\b', re.IGNORECASE)
                match = pattern.search(text_node)
                
                if match:
                    matched_text = match.group(0)
                    new_link = soup.new_tag('a', href=link, target='_blank', rel='noopener sponsored')
                    new_link.string = matched_text
                    new_link['data-affiliate'] = partner
                    
                    before_text = text_node[:match.start()]
                    after_text = text_node[match.end():]
                    
                    parent = text_node.parent
                    text_node.replace_with(before_text)
                    parent.insert(len(parent.contents), new_link)
                    parent.insert(len(parent.contents), after_text)
                    
                    break
        
        return str(soup)
    
    def generate_affiliate_block(self, enrichments):
        """Generate HTML block with affiliate recommendations"""
        if not enrichments:
            return ""
        
        html = '<div class="affiliate-recommendations" style="border: 1px solid #e0e0e0; padding: 20px; margin: 20px 0; background: #f9f9f9;">\n'
        html += '  <h3 style="margin-top: 0;">Recommended Tools & Resources</h3>\n'
        html += '  <ul style="margin: 0; padding-left: 20px;">\n'
        
        for item in enrichments[:3]:
            partner_name = item['partner'].replace('_', ' ').title()
            html += f'    <li><a href="{item["link"]}" target="_blank" rel="noopener sponsored">{partner_name}</a> - {item["keyword"].title()}</li>\n'
        
        html += '  </ul>\n'
        html += '  <p style="font-size: 12px; color: #666; margin-bottom: 0;"><em>Disclosure: This post may contain affiliate links. We may earn a commission when you click through and make a purchase at no additional cost to you.</em></p>\n'
        html += '</div>\n'
        
        return html
    
    def process_content(self, html_content, add_block=True, wrap_links=False):
        """Process content and add affiliate enrichments"""
        enrichments = self.enrich_html_content(html_content)
        
        if not enrichments:
            return {
                'enriched_html': html_content,
                'enrichments': [],
                'affiliate_block': ''
            }
        
        enriched_html = html_content
        
        if wrap_links:
            enriched_html = self.wrap_keywords_with_links(html_content, enrichments)
        
        affiliate_block = ''
        if add_block:
            affiliate_block = self.generate_affiliate_block(enrichments)
            enriched_html = enriched_html + '\n\n' + affiliate_block
        
        return {
            'enriched_html': enriched_html,
            'enrichments': enrichments,
            'affiliate_block': affiliate_block
        }


def example_usage():
    """Example usage of affiliate enricher"""
    enricher = AffiliateEnricher()
    
    sample_html = """
    <h2>Best Security Tools for 2025</h2>
    <p>Protect your devices with a reliable VPN like CyberGhost or NordVPN. 
    For password management, consider using a hardware security key like YubiKey.</p>
    
    <p>Additionally, invest in quality hosting from providers like Namecheap or Hostinger 
    to ensure your website is secure. Don't forget to use Grammarly for writing clear security documentation.</p>
    """
    
    result = enricher.process_content(sample_html, add_block=True, wrap_links=False)
    
    print("Affiliate Enricher - Example Output")
    print("=" * 50)
    print(f"\nFound {len(result['enrichments'])} affiliate opportunities:")
    
    for item in result['enrichments']:
        print(f"  - {item['partner']}: {item['keyword']}")
    
    print("\nGenerated Affiliate Block:")
    print(result['affiliate_block'])


if __name__ == '__main__':
    example_usage()
