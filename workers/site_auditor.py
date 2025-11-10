import requests
import json
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from collections import defaultdict

class SiteAuditor:
    def __init__(self, site_url):
        self.site_url = site_url
        self.sitemap_data = []
        self.content_map = []
        self.internal_links = defaultdict(list)
        
    def fetch_sitemap(self):
        """Fetch and parse sitemap.xml"""
        try:
            sitemap_url = urljoin(self.site_url, '/sitemap_index.xml')
            response = requests.get(sitemap_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            sitemaps = soup.find_all('sitemap')
            
            all_urls = []
            for sitemap in sitemaps:
                loc = sitemap.find('loc')
                if loc and 'post-sitemap' in loc.text:
                    post_response = requests.get(loc.text, timeout=10)
                    post_soup = BeautifulSoup(post_response.content, 'xml')
                    urls = post_soup.find_all('url')
                    
                    for url in urls:
                        loc_tag = url.find('loc')
                        lastmod_tag = url.find('lastmod')
                        if loc_tag:
                            all_urls.append({
                                'url': loc_tag.text,
                                'lastmod': lastmod_tag.text if lastmod_tag else None
                            })
            
            self.sitemap_data = all_urls
            return all_urls
            
        except Exception as e:
            print(f"Error fetching sitemap: {e}")
            return []
    
    def analyze_content(self, url):
        """Analyze a single page for content metrics"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title_text = title.text.strip() if title else ''
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content', '') if meta_desc else ''
            
            h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]
            
            article = soup.find('article') or soup.find('main') or soup.find('body')
            if article:
                text_content = article.get_text(separator=' ', strip=True)
                word_count = len(text_content.split())
            else:
                word_count = 0
            
            internal_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and self.site_url in href:
                    internal_links.append(href)
            
            target_keywords = self.extract_keywords(title_text, h1_tags, h2_tags)
            
            return {
                'url': url,
                'title': title_text,
                'meta_description': meta_description,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'word_count': word_count,
                'internal_links': len(internal_links),
                'target_keywords': target_keywords
            }
            
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
            return None
    
    def extract_keywords(self, title, h1_tags, h2_tags):
        """Extract potential target keywords from title and headings"""
        all_text = ' '.join([title] + h1_tags + h2_tags).lower()
        
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
                     'how', 'what', 'why', 'when', 'where', 'your', 'you', 'i', 'we', 'they'}
        
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        keywords = [w for w in words if w not in stopwords]
        
        keyword_freq = defaultdict(int)
        for kw in keywords:
            keyword_freq[kw] += 1
        
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, freq in sorted_keywords[:5]]
    
    def perform_seo_gap_analysis(self):
        """Identify SEO gaps and content opportunities"""
        gaps = {
            'missing_meta_descriptions': [],
            'thin_content': [],
            'low_internal_linking': [],
            'topic_opportunities': [],
            'keyword_suggestions': []
        }
        
        existing_topics = set()
        for page in self.content_map:
            if not page['meta_description']:
                gaps['missing_meta_descriptions'].append(page['url'])
            
            if page['word_count'] < 500:
                gaps['thin_content'].append({
                    'url': page['url'],
                    'word_count': page['word_count']
                })
            
            if page['internal_links'] < 3:
                gaps['low_internal_linking'].append({
                    'url': page['url'],
                    'internal_links': page['internal_links']
                })
            
            for kw in page['target_keywords']:
                existing_topics.add(kw)
        
        ai_automation_topics = [
            'chatgpt automation', 'make.com tutorials', 'zapier workflows',
            'ai content creation', 'automated security scanning', 'python security scripts',
            'api automation', 'no-code security tools', 'ai threat detection',
            'automated vulnerability scanning', 'security automation python',
            'chatgpt for cybersecurity', 'ai-powered siem', 'automated incident response'
        ]
        
        for topic in ai_automation_topics:
            if not any(word in existing_topics for word in topic.split()):
                gaps['topic_opportunities'].append(topic)
        
        gaps['keyword_suggestions'] = [
            {'keyword': 'cybersecurity automation tools', 'difficulty': 'medium', 'intent': 'commercial'},
            {'keyword': 'ai security monitoring', 'difficulty': 'medium', 'intent': 'informational'},
            {'keyword': 'automated threat response', 'difficulty': 'high', 'intent': 'commercial'},
            {'keyword': 'python security automation scripts', 'difficulty': 'low', 'intent': 'informational'},
            {'keyword': 'no-code cybersecurity workflows', 'difficulty': 'low', 'intent': 'informational'},
        ]
        
        return gaps
    
    def identify_monetization_gaps(self):
        """Identify monetization opportunities"""
        return {
            'affiliate_opportunities': [
                {
                    'topic': 'VPN reviews and comparisons',
                    'partners': ['CyberGhost', 'NordVPN', 'Surfshark'],
                    'placement': 'Product comparison table with affiliate links'
                },
                {
                    'topic': 'Security tools directory',
                    'partners': ['Amazon Associates', 'StackSocial'],
                    'placement': 'Interactive widget with affiliate links'
                },
                {
                    'topic': 'AI writing tools for security documentation',
                    'partners': ['Grammarly', 'Jasper'],
                    'placement': 'Tool recommendations in how-to guides'
                },
                {
                    'topic': 'Hosting and domain security',
                    'partners': ['Namecheap', 'Hostinger', 'Cloudways'],
                    'placement': 'Hosting guides with affiliate comparison'
                }
            ],
            'lead_magnets': [
                'Cybersecurity Career Roadmap PDF',
                'Top 50 Security Tools Checklist',
                'Python Security Scripts Bundle',
                'Make.com Security Automation Templates',
                'Email Security Audit Worksheet'
            ],
            'list_building': [
                'Weekly security news digest subscription',
                'Monthly automation playbook updates',
                'Exclusive tool deals and discounts',
                'Free mini-course on security fundamentals'
            ]
        }
    
    def generate_audit_report(self):
        """Generate complete audit report"""
        print("Fetching sitemap...")
        self.fetch_sitemap()
        
        print(f"Analyzing {len(self.sitemap_data)} pages...")
        for idx, page_data in enumerate(self.sitemap_data[:15], 1):
            print(f"Analyzing page {idx}/15: {page_data['url']}")
            content_data = self.analyze_content(page_data['url'])
            if content_data:
                content_data['lastmod'] = page_data['lastmod']
                self.content_map.append(content_data)
        
        print("Performing SEO gap analysis...")
        seo_gaps = self.perform_seo_gap_analysis()
        
        print("Identifying monetization opportunities...")
        monetization_gaps = self.identify_monetization_gaps()
        
        audit_report = {
            'audit_date': datetime.now().isoformat(),
            'site_url': self.site_url,
            'total_pages_analyzed': len(self.content_map),
            'content_map': self.content_map,
            'seo_gaps': seo_gaps,
            'monetization_gaps': monetization_gaps,
            'summary_stats': {
                'avg_word_count': sum(p['word_count'] for p in self.content_map) / len(self.content_map) if self.content_map else 0,
                'pages_with_meta_desc': sum(1 for p in self.content_map if p['meta_description']),
                'avg_internal_links': sum(p['internal_links'] for p in self.content_map) / len(self.content_map) if self.content_map else 0
            }
        }
        
        return audit_report
    
    def save_audit_json(self, audit_report, filepath='../audit/site_audit.json'):
        """Save audit report as JSON"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2, ensure_ascii=False)
        print(f"Saved audit report to {filepath}")
    
    def generate_summary_markdown(self, audit_report, filepath='../audit/summary.md'):
        """Generate human-readable markdown summary"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        md_content = f"""# RobLoTech Site Audit Summary

**Audit Date:** {audit_report['audit_date']}  
**Site URL:** {audit_report['site_url']}  
**Pages Analyzed:** {audit_report['total_pages_analyzed']}

---

## Summary Statistics

- **Average Word Count:** {audit_report['summary_stats']['avg_word_count']:.0f} words
- **Pages with Meta Descriptions:** {audit_report['summary_stats']['pages_with_meta_desc']}/{audit_report['total_pages_analyzed']}
- **Average Internal Links:** {audit_report['summary_stats']['avg_internal_links']:.1f} per page

---

## Content Map

| Title | Word Count | Internal Links | Last Modified |
|-------|------------|----------------|---------------|
"""
        for page in audit_report['content_map'][:10]:
            title = page['title'][:60] + '...' if len(page['title']) > 60 else page['title']
            lastmod = page.get('lastmod', 'N/A')
            lastmod = lastmod[:10] if lastmod and lastmod != 'N/A' else 'N/A'
            md_content += f"| {title} | {page['word_count']} | {page['internal_links']} | {lastmod} |\n"
        
        md_content += f"\n---\n\n## SEO Gap Analysis\n\n"
        
        md_content += f"### Missing Meta Descriptions ({len(audit_report['seo_gaps']['missing_meta_descriptions'])} pages)\n\n"
        for url in audit_report['seo_gaps']['missing_meta_descriptions'][:5]:
            md_content += f"- {url}\n"
        
        md_content += f"\n### Thin Content ({len(audit_report['seo_gaps']['thin_content'])} pages under 500 words)\n\n"
        for item in audit_report['seo_gaps']['thin_content'][:5]:
            md_content += f"- {item['url']} ({item['word_count']} words)\n"
        
        md_content += f"\n### Topic Opportunities\n\n"
        for topic in audit_report['seo_gaps']['topic_opportunities'][:10]:
            md_content += f"- {topic}\n"
        
        md_content += f"\n### Keyword Suggestions\n\n"
        for kw in audit_report['seo_gaps']['keyword_suggestions']:
            md_content += f"- **{kw['keyword']}** (Difficulty: {kw['difficulty']}, Intent: {kw['intent']})\n"
        
        md_content += f"\n---\n\n## Monetization Gaps\n\n"
        
        md_content += f"### Affiliate Opportunities\n\n"
        for opp in audit_report['monetization_gaps']['affiliate_opportunities']:
            md_content += f"**{opp['topic']}**\n"
            md_content += f"- Partners: {', '.join(opp['partners'])}\n"
            md_content += f"- Placement: {opp['placement']}\n\n"
        
        md_content += f"### Lead Magnet Ideas\n\n"
        for magnet in audit_report['monetization_gaps']['lead_magnets']:
            md_content += f"- {magnet}\n"
        
        md_content += f"\n### List Building Strategies\n\n"
        for strategy in audit_report['monetization_gaps']['list_building']:
            md_content += f"- {strategy}\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Saved summary to {filepath}")


if __name__ == '__main__':
    auditor = SiteAuditor('https://roblotech.com')
    audit_report = auditor.generate_audit_report()
    auditor.save_audit_json(audit_report)
    auditor.generate_summary_markdown(audit_report)
    print("\n✅ Site audit complete!")
