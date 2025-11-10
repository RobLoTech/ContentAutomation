# RobLoTech Content Automation Suite

A comprehensive WordPress content automation system for [RobLoTech.com](https://roblotech.com) - streamlining cybersecurity and automation content creation, distribution, and monetization.

## 🚀 Quick Start

1. **View the Landing Page**  
   Open the web preview to see all deliverables and documentation

2. **Configure WordPress**  
   Create an Application Password in WordPress and add to `.env`:
   ```bash
   WP_USER=your_username
   WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

3. **Test Publishing**  
   ```bash
   cd workers
   python wp_publish.py
   ```

4. **Run Automation**  
   ```bash
   python scheduler.py
   ```

## 📦 What's Included

### 🔧 Automation Workers (`/workers/`)

| Worker | Purpose | Schedule |
|--------|---------|----------|
| `site_auditor.py` | SEO gap analysis, content mapping | Monthly (1st) |
| `news_summarizer.py` | RSS → AI summaries → Google Sheets | Daily 7 AM |
| `affiliate_enricher.py` | Auto-wrap affiliate links | On-demand |
| `wp_publish.py` | WordPress REST API publisher | On-demand |
| `metrics_logger.py` | Track CTR, subs, revenue | Sunday 8 PM |
| `content_backlog_generator.py` | Generate article ideas | One-time |

### 🎨 Embeddable Widgets

- **AI Tools Directory** (`/widgets/tools/`) - 30 curated security/automation tools with search, filter, and pricing
- **Automation Playbooks** (`/widgets/playbooks/`) - 10 ready-to-use security workflow recipes

### 📊 Deliverables

- ✅ **Site Audit** - `/audit/site_audit.json` + `/audit/summary.md` (13 pages analyzed)
- ✅ **Content Backlog** - `/backlog/content_backlog.csv` (25 article ideas across 3 pillars)
- ✅ **Metrics Dashboard** - `/dashboard/index.html` (Chart.js visualizations)
- ✅ **Implementation Guide** - `/docs/IMPLEMENTATION.md` (WordPress REST API examples, Make.com integration)

## 🔗 Integrations

### OpenAI (via Replit AI Integrations)
- **Model:** GPT-4o
- **Usage:** News summarization (120 words max)
- **Billing:** Replit credits (no separate API key needed)

### Google Sheets
- **Tab:** "Inoreader Articles"
- **Purpose:** Deduplication cache + summary storage
- **Columns:** date, title, url, summary, source, source_url, category

### WordPress REST API
- **Authentication:** Basic Auth (Application Passwords)
- **Endpoint:** `/wp-json/wp/v2/posts`
- **Status:** Draft posts by default

## 📈 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Posts/Week | 2-3 | ✅ Automated |
| CTR on Affiliates | ≥3% | 📊 Tracked |
| Newsletter Subs | ≥20/week | 📊 Tracked |
| Traffic Growth | +10% MoM | ⏳ Manual |
| Time on Page | ≥90s | ⏳ Manual |

## 🛠️ Architecture

**Host-Agnostic Design**  
- Workers run on Replit, local machine, VPS, or Make.com
- Widgets are static HTML/JS (embeddable anywhere)
- Publishing always goes to WordPress/Hostinger via REST API
- **Zero vendor lock-in**

**Tech Stack**
- **Backend:** Python 3.11, Flask, feedparser, BeautifulSoup, pandas, gspread
- **Frontend:** Vanilla JavaScript, Tailwind CSS (CDN)
- **Data:** SQLite cache, CSV metrics, Google Sheets sync
- **AI:** OpenAI GPT-4o (via Replit AI Integrations)

## 🚦 Deployment Options

### Option 1: Built-in Scheduler (Recommended)

```bash
python scheduler.py
```

Runs all workers on schedule:
- Daily: News summarizer (7 AM EST)
- Weekly: Metrics logger (Sunday 8 PM EST)
- Monthly: Content audit (1st of month)

### Option 2: Make.com (No-Code)

See `/docs/IMPLEMENTATION.md` for webhook integration blueprint

### Option 3: Cron (VPS/Local)

```cron
0 7 * * * cd /path/to/project/workers && python news_summarizer.py
0 20 * * 0 cd /path/to/project/workers && python metrics_logger.py
0 0 1 * * cd /path/to/project/workers && python site_auditor.py
```

## 📋 Environment Variables

```bash
# WordPress (Required for publishing)
WP_URL=https://roblotech.com
WP_USER=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Google Sheets (Auto-configured by Replit connector)
GOOGLE_SHEET_ID=your_sheet_id

# Affiliate Partners (Optional)
AMAZON_ASSOCIATE_TAG=roblotech-20
STACKSOCIAL_AFFILIATE_ID=your-id
APPSUMO_AFFILIATE_ID=your-id
CYBERGHOST_AFFILIATE_ID=your-id
NAMECHEAP_AFFILIATE_ID=your-id
GRAMMARLY_AFFILIATE_ID=your-id

# OpenAI (Auto-configured by Replit AI Integrations)
OPENAI_API_KEY=auto-set
OPENAI_BASE_URL=auto-set
```

## 🎯 Content Pillars

### 1. AI Tools & Automations (10 articles)
- ChatGPT for cybersecurity use cases
- Make.com security automation tutorials
- No-code security workflows
- AI-powered threat detection

### 2. Security Awareness (9 articles)
- Social engineering prevention
- Password manager comparisons
- Zero trust architecture
- Data breach response

### 3. How-To Workflows (6 articles)
- Python security automation scripts
- Automated vulnerability scanning
- Log analysis with Python
- WordPress security hardening

## 🔒 Security Features

- ✅ Secrets stored in `.env` (never committed)
- ✅ WordPress Basic Auth (Application Passwords)
- ✅ Google Sheets OAuth (Replit connector)
- ✅ Input validation on all scraped content
- ✅ Graceful fallbacks for missing credentials

## 📖 Documentation

- **[IMPLEMENTATION.md](/docs/IMPLEMENTATION.md)** - Complete setup guide with code examples
- **[replit.md](/replit.md)** - Project memory and architecture notes
- **Landing Page** - Accessible at root URL when running `main.py`

## 🎨 Widget Embedding

### WordPress HTML Block

```html
<!-- AI Tools Directory -->
<iframe src="https://roblotech.com/wp-content/uploads/ai-widgets/tools/index.html" 
        width="100%" height="800" frameborder="0"></iframe>

<!-- Automation Playbooks -->
<iframe src="https://roblotech.com/wp-content/uploads/ai-widgets/playbooks/index.html" 
        width="100%" height="1200" frameborder="0"></iframe>

<!-- Metrics Dashboard -->
<iframe src="https://roblotech.com/wp-content/uploads/ai-widgets/dashboard/index.html" 
        width="100%" height="1200" frameborder="0"></iframe>
```

## 🧪 Testing

```bash
# Test site audit
cd workers && python site_auditor.py

# Test news summarizer (without publishing)
cd workers && python news_summarizer.py

# Test WordPress connection
cd workers && python wp_publish.py

# Test affiliate enricher
cd workers && python affiliate_enricher.py

# Test metrics logger
cd workers && python metrics_logger.py
```

## 📦 Dependencies

```
flask
feedparser
beautifulsoup4
pandas
schedule
python-dotenv
requests
lxml
gspread
google-auth
openai
```

## 🤝 Contributing

This project is designed for RobLoTech's specific workflow, but the modular architecture allows easy customization:

1. **Add RSS Feeds:** Modify `config.py` → `RSS_FEEDS`
2. **Change Schedule:** Edit `scheduler.py` timing
3. **Add Affiliate Partners:** Update `config.py` → `AFFILIATE_PARTNERS`
4. **Customize Widgets:** Edit `/widgets/tools/tools.json` or `/widgets/playbooks/playbooks.json`

## 📝 License

Proprietary - Built for RobLoTech.com

---

**Built with ❤️ by Replit Agent**  
**Last Updated:** November 10, 2025
