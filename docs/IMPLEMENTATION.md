# RobLoTech Content Automation - Implementation Guide

## Overview

This automation suite provides a complete content workflow system for your WordPress site at roblotech.com. It runs on Replit but publishes to WordPress/Hostinger with **zero vendor lock-in**.

## Table of Contents

1. [Quick Start](#quick-start)
2. [WordPress REST API Setup](#wordpress-rest-api-setup)
3. [Environment Configuration](#environment-configuration)
4. [Running Workers](#running-workers)
5. [Embedding Widgets](#embedding-widgets)
6. [Make.com Integration](#makecom-integration)
7. [Deployment Options](#deployment-options)

---

## Quick Start

### 1. WordPress Application Password Setup

1. Log in to your WordPress admin at `https://roblotech.com/wp-admin`
2. Go to **Users → Profile**
3. Scroll to **Application Passwords** section
4. Enter a name (e.g., "Replit Automation")
5. Click **Add New Application Password**
6. **Copy the generated password** (you won't see it again!)
7. Save it to your `.env` file

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# WordPress Configuration
WP_URL=https://roblotech.com
WP_USER=your_wordpress_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Google Sheets (automatically configured by Replit connector)
GOOGLE_SHEET_ID=your_sheet_id

# Affiliate Partner IDs (optional, for link wrapping)
AMAZON_ASSOCIATE_TAG=roblotech-20
STACKSOCIAL_AFFILIATE_ID=your-id
APPSUMO_AFFILIATE_ID=your-id
CYBERGHOST_AFFILIATE_ID=your-id
NAMECHEAP_AFFILIATE_ID=your-id
GRAMMARLY_AFFILIATE_ID=your-id
```

### 3. Test WordPress Connection

```bash
cd workers
python wp_publish.py
```

You should see a test post created in your WordPress drafts.

---

## WordPress REST API Setup

### Authentication Methods

**Recommended: Application Passwords (WordPress 5.6+)**

```bash
# Create a post
curl -X POST "https://roblotech.com/wp-json/wp/v2/posts" \
  -u "username:xxxx xxxx xxxx xxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post from API",
    "content": "<p>Hello from the REST API!</p>",
    "status": "draft"
  }'
```

**Response:**
```json
{
  "id": 123,
  "link": "https://roblotech.com/test-post-from-api",
  "status": "draft",
  "title": {
    "rendered": "Test Post from API"
  }
}
```

### Python Example

```python
import requests
import os

WP_URL = "https://roblotech.com"
AUTH = (os.getenv("WP_USER"), os.getenv("WP_APP_PASSWORD"))

def create_post(title, content, status="draft"):
    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        auth=AUTH,
        json={
            "title": title,
            "content": content,
            "status": status
        }
    )
    return response.json()

result = create_post(
    "My Automated Post",
    "<p>This was created via automation!</p>"
)
print(f"Post created: {result['link']}")
```

### Get Categories

```bash
curl "https://roblotech.com/wp-json/wp/v2/categories"
```

### Assign Categories to Post

```python
# Get category ID first
categories = requests.get(f"{WP_URL}/wp-json/wp/v2/categories").json()
cybersecurity_id = [c['id'] for c in categories if c['name'] == 'Cybersecurity'][0]

# Create post with category
create_post("New Post", "<p>Content</p>", categories=[cybersecurity_id])
```

---

## Running Workers

### News Summarizer (Daily at 7 AM EST)

```bash
cd workers
python news_summarizer.py
```

**What it does:**
1. Fetches articles from 9 RSS feeds
2. Deduplicates against both local cache AND Google Sheets (reads existing URLs from "Inoreader Articles" tab)
3. Generates AI summaries (120 words max using GPT-4o)
4. Saves to `data/news_summaries.json` AND appends to Google Sheets
5. Exports WordPress-ready HTML

**Output:** Ready-to-publish draft posts

**Google Sheets Integration:**
- Automatically connects using Replit Google Sheets connector
- Reads all existing rows from "Inoreader Articles" tab to prevent duplicates
- Appends new summaries with columns: date, title, url, summary, source, source_url, category
- Falls back gracefully if GOOGLE_SHEET_ID is not configured

### Affiliate Enricher

```bash
cd workers
python affiliate_enricher.py
```

**What it does:**
1. Scans content for partner keywords
2. Wraps keywords with affiliate links
3. Generates affiliate recommendation blocks

### Metrics Logger (Weekly on Sunday 8 PM EST)

```bash
cd workers
python metrics_logger.py
```

Logs:
- Posts published this week
- CTR on affiliate links
- Newsletter signups
- Revenue estimates

### Complete Publishing Pipeline

```python
from workers.news_summarizer import run_news_summarizer
from workers.affiliate_enricher import AffiliateEnricher
from workers.wp_publish import WordPressPublisher

# 1. Get news summaries
summaries, wp_posts = run_news_summarizer()

# 2. Enrich with affiliate links
enricher = AffiliateEnricher()
for post in wp_posts:
    enriched = enricher.process_content(post['content'], add_block=True)
    post['content'] = enriched['enriched_html']

# 3. Publish to WordPress
publisher = WordPressPublisher()
for post in wp_posts[:3]:  # Publish top 3
    result = publisher.create_post(
        title=post['title'],
        content=post['content'],
        status='draft'
    )
    print(f"Published: {result['post_url']}")
```

---

## Embedding Widgets in WordPress

### Option 1: Upload Files to WordPress

1. Download `/widgets/tools/` and `/widgets/playbooks/` folders
2. Upload to `/wp-content/uploads/ai-widgets/` via FTP or File Manager
3. Add HTML block in WordPress:

```html
<!-- AI Tools Directory -->
<div id="tools-widget"></div>
<script src="https://roblotech.com/wp-content/uploads/ai-widgets/tools/index.html"></script>

<!-- Automation Playbooks -->
<iframe src="https://roblotech.com/wp-content/uploads/ai-widgets/playbooks/index.html" 
        width="100%" height="800" frameborder="0"></iframe>
```

### Option 2: Use Custom HTML Block (Elementor/Gutenberg)

1. Create a new page in WordPress
2. Add **Custom HTML** block
3. Paste the widget HTML directly

### Option 3: Embed Dashboard

```html
<iframe src="https://roblotech.com/wp-content/uploads/ai-widgets/dashboard/index.html" 
        width="100%" height="1200" frameborder="0"></iframe>
```

---

## Make.com Integration

### Blueprint: News Summarizer to WordPress

```json
{
  "name": "Daily Security News to WordPress",
  "flow": [
    {
      "id": 1,
      "module": "builtin:schedule",
      "data": {
        "schedule": "0 7 * * *",
        "timezone": "America/New_York"
      }
    },
    {
      "id": 2,
      "module": "webhook:custom",
      "data": {
        "url": "https://your-replit-url.repl.co/run-summarizer",
        "method": "POST"
      }
    },
    {
      "id": 3,
      "module": "wordpress:createPost",
      "data": {
        "url": "https://roblotech.com",
        "username": "{{env.WP_USER}}",
        "password": "{{env.WP_APP_PASSWORD}}",
        "title": "{{2.title}}",
        "content": "{{2.content}}",
        "status": "draft"
      }
    }
  ]
}
```

### Setup Steps

1. Import blueprint to Make.com
2. Add WordPress connection (use Application Password)
3. Set schedule trigger
4. Test and activate

---

## Deployment Options

### Path A: Built-in Scheduler (Recommended)

The project includes `scheduler.py` which orchestrates all automation workers:

```bash
python scheduler.py
```

**Scheduled Tasks:**
- News Summarizer: Daily at 7:00 AM EST
- Metrics Logger: Every Sunday at 8:00 PM EST
- Content Audit: 1st of each month at midnight

**To run in background:**
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

### Path B: Make.com Webhook (No-Code)

1. Create Make.com scenario
2. Add Webhook trigger
3. Call WordPress REST API module
4. Activate automation

### Path C: Local/VPS Deployment

```bash
# Clone to your server
git clone https://github.com/yourusername/roblotech-automation.git
cd roblotech-automation

# Install dependencies
pip install -r requirements.txt

# Set up cron job
crontab -e
```

Add:
```cron
0 7 * * * cd /path/to/project/workers && python news_summarizer.py
0 20 * * 0 cd /path/to/project/workers && python metrics_logger.py
```

---

## Hostinger Deployment Notes

### File Upload Methods

1. **FTP/SFTP:**
   - Host: `ftp.roblotech.com`
   - Upload widgets to `/public_html/wp-content/uploads/`

2. **File Manager (cPanel):**
   - Log in to Hostinger panel
   - Navigate to File Manager
   - Upload to `/wp-content/uploads/ai-widgets/`

3. **WordPress Media Library:**
   - Not recommended for HTML/JS files
   - Use FTP instead

### WordPress REST API Permissions

If you get authentication errors:

1. Check `.htaccess` for rewrite rules
2. Verify Application Passwords are enabled
3. Test with curl first before using Python

---

## Troubleshooting

### "401 Unauthorized" Error

- Verify Application Password is correct
- Check username is exact (case-sensitive)
- Ensure WordPress is 5.6+ (Application Passwords feature)

### "403 Forbidden" Error

- WordPress REST API may be disabled
- Check with hosting provider
- Add to `.htaccess`:
  ```
  <IfModule mod_rewrite.c>
  RewriteRule ^index\.php$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.php [L]
  </IfModule>
  ```

### Widgets Not Loading

- Check file paths are correct
- Ensure HTTPS is used
- Verify CORS headers if hosted elsewhere

---

## Success Metrics

Track these in `/dashboard/`:

- ✅ 2-3 posts auto-drafted per week
- ✅ CTR ≥ 3% on affiliate blocks
- ✅ Newsletter subs ≥ 20/week
- ✅ Traffic +10% MoM
- ✅ Time on page ≥ 90s

---

## Support & Resources

- **WordPress REST API Docs:** https://developer.wordpress.org/rest-api/
- **Make.com Templates:** https://www.make.com/en/templates
- **Hostinger Knowledge Base:** https://support.hostinger.com/

---

**Built for RobLoTech by Replit Agent**  
**Last Updated:** November 10, 2025
