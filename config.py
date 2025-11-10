import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # WordPress Configuration
    WP_URL = os.getenv('WP_URL', 'https://roblotech.com')
    WP_USER = os.getenv('WP_USER', '')
    WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD', '')
    
    # Google Sheets Configuration
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')
    SHEET_TAB_NAME = 'Inoreader Articles'
    SHEET_COLUMNS = ['date', 'title', 'url', 'summary', 'source', 'source_url', 'category']
    
    # OpenAI Configuration (via Replit AI Integrations)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = 'gpt-4o'
    
    # RSS Feeds
    RSS_FEEDS = [
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
    
    # Affiliate Partner Configuration
    AFFILIATE_PARTNERS = {
        'amazon': {
            'tag': os.getenv('AMAZON_ASSOCIATE_TAG', ''),
            'keywords': ['book', 'device', 'hardware', 'gadget', 'equipment', 'tool'],
            'base_url': 'https://www.amazon.com/s?tag={tag}&k='
        },
        'stacksocial': {
            'id': os.getenv('STACKSOCIAL_AFFILIATE_ID', ''),
            'keywords': ['software', 'productivity', 'app', 'course', 'training'],
            'base_url': 'https://stacksocial.com/?rid={id}'
        },
        'appsumo': {
            'id': os.getenv('APPSUMO_AFFILIATE_ID', ''),
            'keywords': ['saas', 'startup', 'business tool', 'ai tool', 'automation'],
            'base_url': 'https://appsumo.com/?rf={id}'
        },
        'cyberghost': {
            'id': os.getenv('CYBERGHOST_AFFILIATE_ID', ''),
            'keywords': ['vpn', 'privacy', 'encryption', 'anonymity'],
            'base_url': 'https://www.cyberghostvpn.com/?aid={id}'
        },
        'namecheap': {
            'id': os.getenv('NAMECHEAP_AFFILIATE_ID', ''),
            'keywords': ['domain', 'hosting', 'ssl', 'website'],
            'base_url': 'https://www.namecheap.com/?aff={id}'
        },
        'grammarly': {
            'id': os.getenv('GRAMMARLY_AFFILIATE_ID', ''),
            'keywords': ['writing', 'grammar', 'ai writing', 'content creation'],
            'base_url': 'https://www.grammarly.com/?affiliateID={id}'
        }
    }
    
    # Content Settings
    SUMMARY_MAX_LENGTH = int(os.getenv('SUMMARY_MAX_LENGTH', 120))
    POSTS_PER_WEEK_TARGET = int(os.getenv('POSTS_PER_WEEK_TARGET', 3))
    CTR_TARGET = float(os.getenv('CTR_TARGET', 3.0))
    NEWSLETTER_SUBS_TARGET = int(os.getenv('NEWSLETTER_SUBS_TARGET', 20))
    
    # Schedule Settings
    NEWS_SUMMARIZER_TIME = os.getenv('NEWS_SUMMARIZER_TIME', '07:00')
    METRICS_LOGGER_DAY = os.getenv('METRICS_LOGGER_DAY', 'sunday')
    METRICS_LOGGER_TIME = os.getenv('METRICS_LOGGER_TIME', '20:00')
    
    # Data Paths
    DATA_DIR = 'data'
    AUDIT_DIR = 'audit'
    BACKLOG_DIR = 'backlog'
    WIDGETS_DIR = 'widgets'
    DASHBOARD_DIR = 'dashboard'
    DRAFT_POSTS_DIR = 'draft_posts'
