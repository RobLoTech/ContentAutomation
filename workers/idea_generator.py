import os
import json
from datetime import datetime
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

load_dotenv()


def get_sheets_client():
    """Connect to Google Sheets using the same service account JSON."""
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        print("⚠️ GOOGLE_SERVICE_ACCOUNT_JSON not set; Sheets integration disabled")
        return None

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
        print("✅ Connected to Google Sheets (idea generator)")
        return gc
    except Exception as e:
        print(f"⚠️ Failed to initialize Google Sheets client for idea generator: {e}")
        return None


def get_recent_news_rows(gc, max_rows=5):
    """
    Read the newest news rows from 'Inoreader Articles'.
    Assumes sheet is already sorted with newest at the top (which your Apps Script handles).
    """
    try:
        sheet = gc.open("RobLoTech_Content_Ideas").worksheet("Inoreader Articles")
        records = sheet.get_all_records()  # list of dicts, skipping header
        if not records:
            print("⚠️ No news records found in Inoreader Articles")
            return []

        # Take the first N rows = newest N
        recent = records[:max_rows]
        print(f"✅ Fetched {len(recent)} recent news rows for idea generation")
        return recent
    except Exception as e:
        print(f"⚠️ Error reading Inoreader Articles for idea generator: {e}")
        return []


def get_backlog_sheet(gc):
    """Get the Content_Backlog worksheet."""
    try:
        sheet = gc.open("RobLoTech_Content_Ideas").worksheet("Content_Backlog")
        print("✅ Connected to Content_Backlog sheet")
        return sheet
    except Exception as e:
        print(f"⚠️ Error opening Content_Backlog sheet: {e}")
        return None


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not api_key:
        print("⚠️ OPENAI_API_KEY not set; idea generator will not run")
        return None

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client


def build_idea_prompt(news_item):
    """
    Create a prompt for generating ideas from a single news article row.
    Expects keys like: title, url, summary, source, category.
    """
    title = news_item.get("title", "")
    url = news_item.get("url", "")
    summary = news_item.get("clean_summary") or news_item.get("summary", "")
    source = news_item.get("source", "")
    category = news_item.get("Category") or news_item.get("category", "")

    prompt = f"""
You are a senior content strategist and cybersecurity educator helping a solo creator plan monetizable content.

You are given a single news article with this context:

- Title: {title}
- URL: {url}
- Source: {source}
- Topical category: {category}
- Summary: {summary}

Based on this, generate 3 high-quality content ideas that:
- Fit a cybersecurity / AI tools / automation brand
- Are realistic for a solo creator with a full-time job
- Have clear potential for affiliate angles (e.g. VPN, password managers, cloud security tools, M365 security, automation platforms, AI tools)
- Could be blog posts, newsletter issues, or tutorials

Return your answer as VALID JSON ONLY, no commentary, in this format:

[
  {{
    "idea_title": "...",
    "idea_type": "blog_post | newsletter | tutorial | video_script",
    "angle": "...",
    "target_audience": "...",
    "difficulty": "easy | medium | advanced",
    "affiliate_potential": "...",
    "notes": "..."
  }},
  ...
]
"""
    return prompt


def generate_ideas_for_news(client, news_item):
    """Call OpenAI to generate ideas for a single news row and return a list of idea dicts."""
    prompt = build_idea_prompt(news_item)

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity content strategist who outputs valid JSON only."
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )

        raw = response.choices[0].message.content.strip()

        # Try to parse as JSON
        ideas = json.loads(raw)
        if not isinstance(ideas, list):
            print("⚠️ OpenAI response was not a list; skipping this item")
            return []

        print(f"✅ Generated {len(ideas)} ideas for: {news_item.get('title', '')[:60]}...")
        return ideas

    except Exception as e:
        print(f"⚠️ Error generating ideas from OpenAI: {e}")
        return []


def append_ideas_to_backlog(backlog_sheet, news_item, ideas):
    """Append generated ideas into Content_Backlog."""
    if not ideas:
        return 0

    rows = []
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    source_title = news_item.get("title", "")
    source_url = news_item.get("url", "")

    for idea in ideas:
        rows.append([
            now_iso,                               # date
            source_title,                          # source_title
            source_url,                            # source_url
            idea.get("idea_title", ""),            # idea_title
            idea.get("idea_type", ""),             # idea_type
            idea.get("angle", ""),                 # angle
            idea.get("target_audience", ""),       # target_audience
            idea.get("difficulty", ""),            # difficulty
            idea.get("affiliate_potential", ""),   # affiliate_potential
            idea.get("notes", ""),                 # notes
            "new",                                 # status
        ])

    try:
        backlog_sheet.append_rows(rows)
        print(f"✅ Appended {len(rows)} ideas to Content_Backlog")
        return len(rows)
    except Exception as e:
        print(f"⚠️ Error appending ideas to Content_Backlog: {e}")
        return 0


def run_idea_generator(max_news_rows=5):
    """Main entry point to generate ideas from recent news."""
    print("Idea Generator - Starting")
    print("=" * 50)

    client = get_openai_client()
    if not client:
        return

    gc = get_sheets_client()
    if not gc:
        return

    news_rows = get_recent_news_rows(gc, max_rows=max_news_rows)
    if not news_rows:
        print("⚠️ No recent news rows to process")
        return

    backlog_sheet = get_backlog_sheet(gc)
    if not backlog_sheet:
        return

    total_ideas = 0

    for news_item in news_rows:
        ideas = generate_ideas_for_news(client, news_item)
        total_ideas += append_ideas_to_backlog(backlog_sheet, news_item, ideas)

    print("\n📊 Idea generation complete")
    print(f"   News rows processed: {len(news_rows)}")
    print(f"   Ideas added to backlog: {total_ideas}")


if __name__ == "__main__":
    run_idea_generator()
