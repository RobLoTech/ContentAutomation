import os
import json
from datetime import datetime
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

load_dotenv()

# Topics we care about most (mainstream / high-interest)
INTEREST_KEYWORDS = [
    "windows",
    "microsoft",
    "office 365",
    "m365",
    "exchange",
    "azure",
    "active directory",
    "activedirectory",
    "domain controller",
    "powershell",
    "vpn",
    "cisco",
    "anyconnect",
    "firepower",
    "okta",
    "duo",
    "single sign-on",
    "sso",
    "google workspace",
    "workspace",
    "macos",
    "ios",
    "iphone",
    "android",
    "chrome",
    "browser",
    "cloud",
    "aws",
    "amazon web services",
    "gcp",
    "google cloud",
    "iam",
    "identity",
    "ransomware",
    "data breach",
    "zero-day",
    "zeroday",
    "phishing",
    "business email compromise",
    "bec",
    "password manager",
    "vpn service",
    "email security",
    "mfa",
    "multi-factor",
]

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

def matches_interest_keywords(news_item: dict) -> bool:
    """
    Return True if the news item looks broadly interesting / mainstream
    based on simple keyword matching in title/summary/source/category.
    """
    text_parts = [
        news_item.get("title", ""),
        news_item.get("summary", ""),
        news_item.get("clean_summary", ""),
        news_item.get("source", ""),
        news_item.get("Category", ""),
        news_item.get("category", ""),
    ]

    haystack = " ".join([p for p in text_parts if p]).lower()

    for kw in INTEREST_KEYWORDS:
        if kw.lower() in haystack:
            return True

    return False

def compute_keyword_counts(records):
    """
    For a list of news records, count how many times each interest keyword appears
    across the newest articles. This gives us a simple 'trend strength' measure.
    """
    counts = {kw.lower(): 0 for kw in INTEREST_KEYWORDS}

    for row in records:
        text_parts = [
            row.get("title", ""),
            row.get("summary", ""),
            row.get("clean_summary", ""),
            row.get("source", ""),
            row.get("Category", ""),
            row.get("category", ""),
        ]
        haystack = " ".join([p for p in text_parts if p]).lower()

        for kw in INTEREST_KEYWORDS:
            key = kw.lower()
            if key in haystack:
                counts[key] += 1

    return counts


def trend_score_for_item(news_item: dict, keyword_counts: dict) -> int:
    """
    Compute a simple trend score for a single news item:
    - For every interest keyword that appears in this item,
      look up how often that keyword appears across the recent articles.
    - The score is the max of those frequencies.
      (e.g. if 'microsoft' appears in 5 recent items and 'ransomware' in 3,
       the trend_score is 5.)
    """
    text_parts = [
        news_item.get("title", ""),
        news_item.get("summary", ""),
        news_item.get("clean_summary", ""),
        news_item.get("source", ""),
        news_item.get("Category", ""),
        news_item.get("category", ""),
    ]
    haystack = " ".join([p for p in text_parts if p]).lower()

    score = 0
    for kw in INTEREST_KEYWORDS:
        key = kw.lower()
        if key in haystack:
            freq = keyword_counts.get(key, 0)
            if freq > score:
                score = freq

    return score

def get_recent_news_rows(gc, max_rows=5, scan_depth=30):
    """
    Read the newest news rows from 'Inoreader Articles',
    then filter to only those that match our interest keywords.

    - scan_depth: how many newest rows to scan (e.g. 30)
    - max_rows: maximum number of matching rows to return
    """
    try:
        sheet = gc.open("RobLoTech_Content_Ideas").worksheet("Inoreader Articles")
        records = sheet.get_all_records()  # list of dicts, skipping header
        if not records:
            print("⚠️ No news records found in Inoreader Articles")
            return []

        # Look at the newest `scan_depth` articles
        recent_candidates = records[:scan_depth]

        # Filter by our interest keywords
        filtered = [row for row in recent_candidates if matches_interest_keywords(row)]

        if not filtered:
            print(f"⚠️ No recent articles matched interest keywords in the newest {scan_depth} rows")
            return []

        # Limit to max_rows
        selected = filtered[:max_rows]
        print(
            f"✅ Fetched {len(selected)} high-interest news rows for idea generation "
            f"(from {scan_depth} newest articles, {len(filtered)} matched keywords)"
        )
        return selected

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
You are a senior content strategist and cybersecurity educator helping a solo creator
build a monetized content engine.

You are given a single news article with this context:

- Title: {title}
- URL: {url}
- Source: {source}
- Topical category: {category}
- Summary: {summary}

Your goals:
- Fit a cybersecurity / AI tools / automation brand
- Focus on topics that appeal to a broad audience (IT pros, security-curious tech users, SMBs)
- Be realistic for a solo creator with a full-time job
- Maximize monetization and affiliate potential where it makes sense

Generate EXACTLY 3 high-quality content ideas for this article.

Each idea MUST:
- Use one of these EXACT idea_type values:
  - "tutorial"           (step-by-step guides, how-tos, labs, walkthroughs)
  - "newsletter"         (curated updates, opinion, weekly digest)
  - "tool_review"        (deep dives, comparisons, “best tools for X”)
  - "cheat_sheet"        (concise reference, checklists, one-pagers)
- Include a clear angle that explains the hook (e.g. "What SMBs can learn from this breach")
- Specify a clear target_audience (e.g. "SMB IT managers", "non-technical executives", "junior security analysts")
- Include difficulty as "easy", "medium", or "advanced" for the creator
- Explicitly describe affiliate_potential, mentioning concrete categories when relevant, such as:
  - VPNs, password managers, email security, endpoint security, XDR/EDR
  - cloud security tools (AWS/Azure/GCP), M365 security, backup/DR tools
  - training platforms, courses, books, newsletters, automation tools
- Provide notes that give extra implementation detail (e.g. suggested sections, example tools, or how it ties back to the news article).

Return your answer as VALID JSON ONLY, with NO extra commentary, in this format:

[
  {{
    "idea_title": "string - compelling title that could be used for the piece",
    "idea_type": "tutorial | newsletter | tool_review | cheat_sheet",
    "angle": "string - what makes this idea interesting, unique, or timely",
    "target_audience": "string - who this content is aimed at",
    "difficulty": "easy | medium | advanced",
    "affiliate_potential": "string - describe realistic affiliate angles, or say 'low' if not a good fit",
    "notes": "string - extra implementation details, suggested sections, tools, or calls to action"
  }},
  ...
]
"""
    return prompt

def extract_json_block(raw: str) -> str:
    """
    Try to clean the OpenAI response so it's valid JSON:
    - Remove ```json ... ``` fences if present
    - Trim everything before the first '[' or '{'
    """
    if not raw:
        return raw

    text = raw.strip()

    # Strip code fences like ```json ... ``` or ``` ...
    if text.startswith("```"):
        lines = text.splitlines()

        # Remove the first line (``` or ```json)
        lines = lines[1:]

        # If last line is ``` remove it
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Find the first JSON-looking character
    first_idx = None
    for ch in ["[", "{"]:
        idx = text.find(ch)
        if idx != -1:
            if first_idx is None or idx < first_idx:
                first_idx = idx

    if first_idx is not None:
        text = text[first_idx:].strip()

    return text

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
        cleaned = extract_json_block(raw)

        # Try to parse as JSON
        ideas = json.loads(cleaned)

        if not isinstance(ideas, list):
            print("⚠️ OpenAI response was not a list; skipping this item")
            return []

        print(f"✅ Generated {len(ideas)} ideas for: {news_item.get('title', '')[:60]}...")
        return ideas

    except Exception as e:
        print(f"⚠️ Error generating ideas from OpenAI: {e}")
        return []

def get_existing_titles(backlog_sheet):
    """
    Load existing idea titles from Content_Backlog so we don't create duplicates.
    Titles are normalized to lowercase for comparison.
    """
    try:
        records = backlog_sheet.get_all_records()
        titles = set()

        for row in records:
            title = row.get("idea_title")
            if title:
                norm = title.strip().lower()
                if norm:
                    titles.add(norm)

        print(f"✅ Loaded {len(titles)} existing idea titles from Content_Backlog")
        return titles
    except Exception as e:
        print(f"⚠️ Error reading existing ideas from Content_Backlog: {e}")
        return set()

def append_ideas_to_backlog(backlog_sheet, news_item, ideas, existing_titles=None):
    """Append generated ideas into Content_Backlog, skipping duplicate titles."""
    if not ideas:
        return 0

    if existing_titles is None:
        existing_titles = set()

    rows = []
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    source_title = news_item.get("title", "")
    source_url = news_item.get("url", "")

    skipped = 0

    for idea in ideas:
        raw_title = idea.get("idea_title", "")
        norm_title = raw_title.strip().lower() if raw_title else ""

        # Skip ideas with no usable title
        if not norm_title:
            continue

        # Skip duplicates
        if norm_title in existing_titles:
            skipped += 1
            continue

        # Record this title so we don't reuse it later in the same run
        existing_titles.add(norm_title)

        rows.append([
            now_iso,                               # date
            source_title,                          # source_title
            source_url,                            # source_url
            raw_title,                             # idea_title
            idea.get("idea_type", ""),             # idea_type
            idea.get("angle", ""),                 # angle
            idea.get("target_audience", ""),       # target_audience
            idea.get("difficulty", ""),            # difficulty
            idea.get("affiliate_potential", ""),   # affiliate_potential
            idea.get("notes", ""),                 # notes
            "new",                                 # status
        ])

    if not rows:
        print("⚠️ No non-duplicate ideas to append for this news item")
        return 0

    try:
        backlog_sheet.append_rows(rows)
        print(f"✅ Appended {len(rows)} ideas to Content_Backlog (skipped {skipped} duplicates)")
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

    # Load existing titles once per run for de-duplication
    existing_titles = get_existing_titles(backlog_sheet)

    total_ideas = 0

    for news_item in news_rows:
        ideas = generate_ideas_for_news(client, news_item)
        total_ideas += append_ideas_to_backlog(backlog_sheet, news_item, ideas, existing_titles)

    print("\n📊 Idea generation complete")
    print(f"   News rows processed: {len(news_rows)}")
    print(f"   Ideas added to backlog: {total_ideas}")


if __name__ == "__main__":
    run_idea_generator()
