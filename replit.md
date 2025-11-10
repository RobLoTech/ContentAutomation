# RobLoTech Content Automation Suite

## Project Overview

**Purpose:** Comprehensive WordPress content automation system for RobLoTech.com - a cybersecurity and automation blog  
**Tech Stack:** Python (Flask, feedparser, OpenAI, beautifulsoup4, pandas), JavaScript (Vanilla), Tailwind CSS  
**Current State:** MVP complete with all automation workers, widgets, dashboard, and documentation  
**Last Updated:** November 10, 2025

## Project Architecture

### Core Components

1. **Automation Workers** (`/workers/`)
   - `site_auditor.py` - Crawls roblotech.com sitemap, analyzes content (word count, meta, keywords), identifies SEO gaps
   - `news_summarizer.py` - Fetches 9 RSS feeds (Bleeping Computer, Dark Reading, etc.), deduplicates, generates AI summaries (GPT-4o via Replit AI Integrations)
   - `affiliate_enricher.py` - Scans content for keywords, wraps with affiliate links (Amazon, StackSocial, AppSumo, VPN providers, hosting, AI writing tools)
   - `wp_publish.py` - WordPress REST API publisher using Basic Auth (Application Passwords)
   - `metrics_logger.py` - Weekly metrics tracking (posts/week, CTR, newsletter subs, revenue)
   - `content_backlog_generator.py` - Generates 25 article ideas across 3 content pillars

2. **Embeddable Widgets** (`/widgets/`)
   - AI Tools Directory (`/tools/`) - 30 pre-seeded security/automation tools with filtering
   - Automation Playbooks (`/playbooks/`) - 10 ready-to-use security workflow recipes

3. **Analytics Dashboard** (`/dashboard/`)
   - Metrics visualization (Chart.js)
   - Success criteria tracking (posts/week, CTR, subs, revenue)
   - Top posts table

4. **Documentation** (`/docs/`)
   - IMPLEMENTATION.md - Complete setup guide (WordPress REST API, Make.com integration, deployment options)

### Integration Setup

- **OpenAI:** Connected via Replit AI Integrations (python_openai_ai_integrations) - No API key needed, billed to Replit credits
- **Google Sheets:** Connected via Replit connector (conn_google-sheet_01K9QGBDEJW6GNYRYVS1TYYDJQ) for news article storage
- **WordPress:** REST API v2 using Application Passwords (requires WP_USER and WP_APP_PASSWORD in .env)

## Recent Changes (Nov 10, 2025)

### Critical Fixes Applied

1. ✅ **Google Sheets Integration** - news_summarizer.py now:
   - Reads existing articles from Google Sheets on initialization
   - Deduplicates against both local cache AND Sheets URLs
   - Appends new summaries to the configured "Inoreader Articles" tab
   - Gracefully falls back if GOOGLE_SHEET_ID is not set

2. ✅ **Flask Widget Routing** - Fixed widget serving:
   - Added explicit routes for `/widgets/tools/` and `/widgets/playbooks/`
   - Both now correctly serve their respective index.html files
   - Widgets are fully accessible from the main landing page

3. ✅ **Scheduler/Workflow Integration** - Created scheduler.py:
   - Daily news summarizer at 7:00 AM EST
   - Weekly metrics logger on Sunday at 8:00 PM EST
   - Monthly content audit on 1st of each month
   - Can run standalone or be triggered via Make.com

### Completed Deliverables

1. ✅ Site audit system - Generated `/audit/site_audit.json` and `/audit/summary.md` with:
   - 13 pages analyzed from roblotech.com
   - SEO gap analysis (missing meta descriptions, thin content, topic opportunities)
   - Monetization gaps (affiliate opportunities, lead magnets, list building strategies)

2. ✅ Content backlog - Generated `/backlog/content_backlog.csv` with 25 articles:
   - 10 AI Tools & Automations articles (ChatGPT for cybersecurity, Make.com tutorials, etc.)
   - 9 Security Awareness articles (social engineering, password managers, zero trust, etc.)
   - 6 How-To Workflows articles (Python security scripts, automation recipes, etc.)

3. ✅ All 5 automation workers implemented and tested
4. ✅ AI Tools Directory widget with 30 tools (ChatGPT, Grammarly, Make.com, CyberGhost, etc.)
5. ✅ Automation Playbooks widget with 10 recipes (daily security news, phishing detection, etc.)
6. ✅ Metrics dashboard with Chart.js visualizations
7. ✅ Complete implementation guide with WordPress REST API examples, Make.com blueprint, deployment options

## User Preferences

- **Content Focus:** Cybersecurity education for both IT pros and non-technical users, AI automation tools, practical how-to guides
- **Monetization:** Affiliate marketing (6 partner programs), newsletter growth (target: 20 subs/week)
- **Publishing:** WordPress/Hostinger deployment (no Replit hosting dependency)
- **Automation Schedule:**
  - News summarizer: Daily at 7 AM EST
  - Metrics logger: Sunday 8 PM EST
  - Content audit: Monthly

## Environment Configuration

### Required .env Variables

```
# WordPress
WP_URL=https://roblotech.com
WP_USER=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Google Sheets (auto-configured by connector)
GOOGLE_SHEET_ID=your_sheet_id

# Affiliate Partners
AMAZON_ASSOCIATE_TAG=roblotech-20
STACKSOCIAL_AFFILIATE_ID=your-id
APPSUMO_AFFILIATE_ID=your-id
CYBERGHOST_AFFILIATE_ID=your-id
NAMECHEAP_AFFILIATE_ID=your-id
GRAMMARLY_AFFILIATE_ID=your-id

# OpenAI (auto-configured by Replit AI Integrations)
OPENAI_API_KEY=auto-set
OPENAI_BASE_URL=auto-set
```

## Success Metrics (Goals)

- ✅ 2-3 quality posts auto-drafted per week
- ✅ CTR ≥ 3% on affiliate blocks
- ✅ Newsletter subs ≥ 20/week
- ⏳ Traffic +10% MoM
- ⏳ Time on page ≥ 90s

## Deployment Notes

**Host-Agnostic Design:** All widgets export as static HTML/JS. Workers can run on Replit, local machine, VPS, or triggered via Make.com webhooks. Publishing always goes to WordPress REST API at roblotech.com (Hostinger hosting).

**Workflow:** web-server running Flask on port 5000, serving deliverables and documentation hub

## Next Steps

1. User needs to configure WordPress Application Password and update .env
2. Test WordPress publishing with `python workers/wp_publish.py`
3. Upload widgets to WordPress `/wp-content/uploads/ai-widgets/`
4. Set up cron jobs or Make.com scenarios for scheduled automation
5. Review and customize the 25 article ideas in content backlog
