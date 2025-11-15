import feedparser
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import json
import hashlib
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

class NewsSummarizer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.max_length = int(os.getenv('SUMMARY_MAX_LENGTH', 120))
        self.rss_feeds = self.load_feeds()
        self.cache_file = '../data/processed_articles.json'
        self.google_sheet = None

        # --- Google Sheets setup via service account ---
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not creds_json:
            print("⚠️ GOOGLE_SERVICE_ACCOUNT_JSON not set; Sheets integration disabled")
        else:
            try:
                creds_info = json.loads(creds_json)
                creds = Credentials.from_service_account_info(
                    creds_info,
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive",
                    ],
                )
                gc = gspread.authorize(creds)
                # Use your actual sheet + tab names
                sheet = gc.open("RobLoTech_Content_Ideas").worksheet("Inoreader Articles")
                self.google_sheet = sheet
                print("✅ Connected to Google Sheet: RobLoTech_Content_Ideas / Inoreader Articles")
            except Exception as e:
                print(f"⚠️ Failed to initialize Google Sheets client: {e}")
                self.google_sheet = None

        # Load processed URLs AFTER Google Sheets is set up
        self.processed_urls = self.load_processed_cache()
    
    def load_feeds(self):
        """Load RSS feeds from config"""
        return [
            {'url': 'https://feeds.feedburner.com/TheHackersNews', 'name': 'The Hacker News', 'category': 'cybersecurity'},
            {'url': 'https://www.bleepingcomputer.com/feed/', 'name': 'Bleeping Computer', 'category': 'cybersecurity'},
            {'url': 'https://www.darkreading.com/rss.xml', 'name': 'Dark Reading', 'category': 'cybersecurity'},
            {'url': 'https://www.csoonline.com/index.rss', 'name': 'CSO Online', 'category': 'cybersecurity'},
            {'url': 'https://securityaffairs.com/feed', 'name': 'Security Affairs', 'category': 'cybersecurity'},
            {'url': 'https://www.schneier.com/blog/atom.xml', 'name': 'Schneier on Security', 'category': 'cybersecurity'},
            {'url': 'https://www.techradar.com/rss/news', 'name': 'TechRadar', 'category': 'technology'},
            {'url': 'https://venturebeat.com/category/ai/feed/', 'name': 'VentureBeat AI', 'category': 'ai'},
            {'url': 'https://www.makeuseof.com/tag/automation/feed/', 'name': 'MakeUseOf Automation', 'category': 'automation'},
        ]

    def get_source_homepage(self, source_name):
        """Return publisher homepage URL based on source name."""
        mapping = {
            "The Hacker News": "https://thehackernews.com",
            "Bleeping Computer": "https://www.bleepingcomputer.com",
            "Dark Reading": "https://www.darkreading.com",
            "CSO Online": "https://www.csoonline.com",
            "Security Affairs": "https://securityaffairs.com",
            "Schneier on Security": "https://www.schneier.com",
            "TechRadar": "https://www.techradar.com",
            "VentureBeat AI": "https://venturebeat.com",
            "MakeUseOf Automation": "https://www.makeuseof.com",
        }
        return mapping.get(source_name, "")
    
    def load_processed_cache(self):
        """Load cache of already processed article URLs from local cache AND Google Sheets"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        processed_urls = set()
        
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                processed_urls = set(json.load(f))
        
        if self.google_sheet:
            try:
                existing_rows = self.google_sheet.get_all_records()
                for row in existing_rows:
                    if row.get('url'):
                        processed_urls.add(self.generate_url_hash(row['url']))
                print(f"✅ Loaded {len(existing_rows)} existing articles from Google Sheets")
            except Exception as e:
                print(f"⚠️  Could not read from Google Sheets: {e}")
        
        return processed_urls
    
    def save_processed_cache(self):
        """Save processed URLs to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(list(self.processed_urls), f)
    
    def generate_url_hash(self, url):
        """Generate hash for URL deduplication"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def fetch_rss_entries(self, feed_url, max_entries=5):
        """Fetch entries from RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            entries = []
            
            for entry in feed.entries[:max_entries]:
                url = entry.get('link', '')
                url_hash = self.generate_url_hash(url)
                
                if url_hash in self.processed_urls:
                    continue
                
                entries.append({
                    'title': entry.get('title', 'Untitled'),
                    'url': url,
                    'url_hash': url_hash,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:500]
                })
            
            return entries
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
            return []
    
    def summarize_with_ai(self, title, content):
        """Generate AI summary using OpenAI"""
        try:
            prompt = f"""Summarize this cybersecurity/tech news article in exactly {self.max_length} words or less.
Focus on the key facts, impact, and takeaways. Write in a clear, engaging style for IT professionals and non-technical readers.

Title: {title}

Content: {content}

Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity journalist who creates concise, accurate news summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"AI summarization error: {e}")
            return content[:self.max_length] + "..."
    
    def process_all_feeds(self):
        """Process all RSS feeds and generate summaries"""
        all_summaries = []
        
        print(f"Processing {len(self.rss_feeds)} RSS feeds...")
        
        for feed_config in self.rss_feeds:
            print(f"\n📰 {feed_config['name']}...")
            entries = self.fetch_rss_entries(feed_config['url'])
            
            print(f"   Found {len(entries)} new articles")
            
            for entry in entries:
                print(f"   Summarizing: {entry['title'][:60]}...")
                
                summary = self.summarize_with_ai(entry['title'], entry['summary'])
                
                all_summaries.append({
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'title': entry['title'],
                    'url': entry['url'],
                    'summary': summary,
                    'source': feed_config['name'],
                    'source_url': self.get_source_homepage(feed_config['name']),
                    'category': feed_config['category']
                })
                
                self.processed_urls.add(entry['url_hash'])
        
        self.save_processed_cache()
        return all_summaries
    
    def save_summaries_to_file(self, summaries, filepath='../data/news_summaries.json'):
        """Save summaries to JSON file AND Google Sheets"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        existing_data = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                existing_data = json.load(f)
        
        existing_data.extend(summaries)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(summaries)} summaries to {filepath}")
        
        if self.google_sheet and summaries:
            try:
                rows_to_append = []
                for summary in summaries:
                    rows_to_append.append([
                        # 1: date
                        summary.get('date', ''),
                        # 2: title
                        summary.get('title', ''),
                        # 3: url
                        summary.get('url', ''),
                        # 4: summary (we'll use the AI summary here)
                        summary.get('summary', ''),
                        # 5: source
                        summary.get('source', ''),
                        # 6: clean_summary (also AI summary for now)
                        summary.get('summary', ''),
                        # 7: image_url (leave blank for now)
                        '',
                        # 8: web_source_url (use source_url if present, else blank)
                        summary.get('source_url', ''),
                        # 9–12: NeedsCap, EndsWrong, TooShort, TooManySentences
                        '', '', '', '',
                        # 13: Category
                        summary.get('category', ''),
                    ])

                
                self.google_sheet.append_rows(rows_to_append)
                print(f"✅ Appended {len(rows_to_append)} summaries to Google Sheets")
            except Exception as e:
                print(f"⚠️  Could not write to Google Sheets: {e}")
    
    def export_for_wordpress(self, summaries):
        """Format summaries for WordPress publishing"""
        wp_posts = []
        
        for item in summaries:
            html_content = f"""
<p>{item['summary']}</p>

<p><strong>Source:</strong> <a href="{item['url']}" target="_blank" rel="noopener">{item['source']}</a></p>

<p><em>Category: {item['category'].title()} | Published: {item['date']}</em></p>
"""
            wp_posts.append({
                'title': item['title'],
                'content': html_content,
                'category': item['category'],
                'source_url': item['url']
            })
        
        return wp_posts


def run_news_summarizer():
    """Main function to run news summarizer"""
    summarizer = NewsSummarizer()
    
    summaries = summarizer.process_all_feeds()
    
    if summaries:
        summarizer.save_summaries_to_file(summaries)
        wp_posts = summarizer.export_for_wordpress(summaries)
        
        print(f"\n📊 Summary Statistics:")
        print(f"   Total summaries: {len(summaries)}")
        print(f"   Ready for WordPress: {len(wp_posts)}")
        
        return summaries, wp_posts
    else:
        print("\n⚠️  No new articles to process")
        return [], []


if __name__ == '__main__':
    print("News Summarizer - Daily Automation")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("   AI summarization will use fallback method")
    
    run_news_summarizer()
