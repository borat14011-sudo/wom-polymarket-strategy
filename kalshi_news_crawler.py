"""
Kalshi News Crawler & Edge Finder
Scans free public news feeds for signals relevant to Kalshi prediction markets.
No API keys needed - uses Google News RSS and Reddit JSON.
"""

import sys
import os
import json
import time
import hashlib
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests

WORKSPACE = Path(__file__).parent
SIGNALS_JSON = WORKSPACE / "kalshi_news_signals.json"
SIGNALS_MD = WORKSPACE / "kalshi_news_signals.md"
HISTORY_JSON = WORKSPACE / "kalshi_signal_history.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ---------------------------------------------------------------------------
# Market categories and their search queries
# ---------------------------------------------------------------------------
MARKET_CATEGORIES = {
    "Trump Tariffs": {
        "queries": ["Trump tariff", "Trump trade war", "Trump China tariff", "Trump import duty"],
        "subreddits": ["politics", "economics", "wallstreetbets"],
        "keywords": ["tariff", "trade war", "import duty", "customs", "trade deal", "trade policy"],
        "kalshi_markets": [
            "Will Trump impose new tariffs?",
            "US-China trade escalation",
            "New tariff announcement by end of month",
        ],
    },
    "Trump Executive Orders": {
        "queries": ["Trump executive order", "Trump deportation", "Trump immigration order"],
        "subreddits": ["politics", "law", "immigration"],
        "keywords": ["executive order", "deportation", "immigration", "border", "asylum", "ICE"],
        "kalshi_markets": [
            "Trump executive order count",
            "Mass deportation operation",
        ],
    },
    "Greenland": {
        "queries": ["Trump Greenland", "US Greenland acquisition", "Denmark Greenland"],
        "subreddits": ["geopolitics", "worldnews"],
        "keywords": ["greenland", "denmark", "arctic", "acquisition", "purchase", "territory"],
        "kalshi_markets": [
            "Will the US acquire Greenland?",
        ],
    },
    "Supreme Court": {
        "queries": ["Supreme Court ruling", "SCOTUS decision", "Supreme Court case"],
        "subreddits": ["scotus", "law", "politics"],
        "keywords": ["supreme court", "scotus", "ruling", "decision", "opinion", "dissent", "justice"],
        "kalshi_markets": [
            "Supreme Court landmark ruling",
        ],
    },
    "Fed Rate Decision": {
        "queries": ["Federal Reserve rate decision", "Fed interest rate", "FOMC meeting", "Fed rate cut"],
        "subreddits": ["economics", "wallstreetbets", "investing"],
        "keywords": ["fed", "fomc", "interest rate", "rate cut", "rate hike", "monetary policy", "powell", "inflation"],
        "kalshi_markets": [
            "Fed rate decision next meeting",
            "Number of rate cuts this year",
        ],
    },
    "GTA VI": {
        "queries": ["GTA 6 release date", "GTA VI news", "Rockstar GTA"],
        "subreddits": ["GTA6", "gaming", "Games"],
        "keywords": ["gta 6", "gta vi", "rockstar", "grand theft auto", "release date", "delay", "trailer"],
        "kalshi_markets": [
            "GTA VI release date",
            "Will GTA VI be delayed?",
        ],
    },
    "SpaceX": {
        "queries": ["SpaceX launch", "SpaceX Starship", "SpaceX IPO"],
        "subreddits": ["spacex", "space"],
        "keywords": ["spacex", "starship", "falcon", "launch", "ipo", "musk", "orbital"],
        "kalshi_markets": [
            "SpaceX successful Starship launch",
            "SpaceX IPO",
        ],
    },
    "Tech IPOs": {
        "queries": ["tech IPO 2026", "upcoming IPO", "Stripe IPO", "Reddit IPO"],
        "subreddits": ["wallstreetbets", "stocks", "investing"],
        "keywords": ["ipo", "public offering", "listing", "debut", "valuation"],
        "kalshi_markets": [
            "Major tech IPO this quarter",
        ],
    },
    "Israel Geopolitics": {
        "queries": ["Israel PM Netanyahu", "Israel ceasefire", "Israel Hamas", "Israel war"],
        "subreddits": ["worldnews", "geopolitics"],
        "keywords": ["israel", "netanyahu", "hamas", "ceasefire", "gaza", "hezbollah", "hostage"],
        "kalshi_markets": [
            "Israel ceasefire agreement",
            "Netanyahu remains PM",
        ],
    },
    "EU Politics": {
        "queries": ["EU election", "European Union policy", "EU regulation"],
        "subreddits": ["europe", "geopolitics"],
        "keywords": ["eu", "european union", "brussels", "regulation", "election", "parliament"],
        "kalshi_markets": [
            "EU policy change",
        ],
    },
    "US Elections": {
        "queries": ["2026 midterm election", "US Senate race", "US election polls"],
        "subreddits": ["politics", "fivethirtyeight"],
        "keywords": ["election", "midterm", "senate", "house", "poll", "primary", "candidate", "ballot"],
        "kalshi_markets": [
            "2026 midterm results",
            "Senate control after midterms",
        ],
    },
}


def fetch_google_news(query, max_items=10):
    """Fetch articles from Google News RSS."""
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source = item.findtext("source", "")
            items.append({
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "source": source,
                "origin": "google_news",
            })
        return items
    except Exception as e:
        print(f"  [WARN] Google News fetch failed for '{query}': {e}")
        return []


def fetch_reddit(subreddit, max_items=10):
    """Fetch hot posts from a subreddit."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={max_items}"
    try:
        resp = requests.get(url, headers={"User-Agent": "KalshiCrawler/1.0 (by /u/kalshicrawler)"}, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            items.append({
                "title": d.get("title", ""),
                "link": f"https://reddit.com{d.get('permalink', '')}",
                "pub_date": datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z"),
                "source": f"r/{subreddit}",
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
                "origin": "reddit",
            })
        return items
    except Exception as e:
        print(f"  [WARN] Reddit fetch failed for r/{subreddit}: {e}")
        return []


def compute_relevance(article, keywords):
    """Score 0-100 how relevant an article is to a market category."""
    title_lower = article["title"].lower()
    score = 0
    matched = 0
    for kw in keywords:
        if kw.lower() in title_lower:
            matched += 1
    if matched == 0:
        return 0
    # Base score from keyword matches
    score = min(matched * 25, 60)
    # Recency boost
    try:
        from email.utils import parsedate_to_datetime
        pub_dt = parsedate_to_datetime(article["pub_date"])
        age_hours = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
        if age_hours < 2:
            score += 30
        elif age_hours < 6:
            score += 20
        elif age_hours < 24:
            score += 10
    except Exception:
        score += 5  # unknown date, small bonus
    # Reddit engagement boost
    if article.get("origin") == "reddit":
        reddit_score = article.get("score", 0)
        if reddit_score > 1000:
            score += 10
        elif reddit_score > 100:
            score += 5
    return min(score, 100)


def estimate_edge(article, category_name):
    """
    Heuristic edge estimation.
    Returns a string: HIGH / MEDIUM / LOW / NONE
    High edge = very recent + high relevance + likely not priced in.
    """
    try:
        from email.utils import parsedate_to_datetime
        pub_dt = parsedate_to_datetime(article["pub_date"])
        age_hours = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
    except Exception:
        age_hours = 999

    relevance = article.get("relevance_score", 0)

    if relevance >= 70 and age_hours < 2:
        return "HIGH"
    elif relevance >= 50 and age_hours < 6:
        return "MEDIUM"
    elif relevance >= 30 and age_hours < 24:
        return "LOW"
    return "NONE"


def article_id(article):
    """Deterministic ID for deduplication."""
    raw = (article.get("title", "") + article.get("link", "")).encode()
    return hashlib.md5(raw).hexdigest()[:12]


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def crawl_all():
    """Main crawl loop across all categories."""
    print("=" * 60, flush=True)
    print("KALSHI NEWS CRAWLER & EDGE FINDER", flush=True)
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("=" * 60, flush=True)

    all_signals = []
    seen_ids = set()

    sys.stdout.flush()
    for cat_name, cat_cfg in MARKET_CATEGORIES.items():
        print(f"\n--- {cat_name} ---", flush=True)

        articles = []

        # Google News (use first 2 queries for speed)
        for q in cat_cfg["queries"][:2]:
            fetched = fetch_google_news(q, max_items=5)
            articles.extend(fetched)
            time.sleep(0.3)

        # Reddit (first subreddit only for speed)
        for sub in cat_cfg["subreddits"][:1]:
            fetched = fetch_reddit(sub, max_items=5)
            articles.extend(fetched)
            time.sleep(0.3)

        # Score and filter
        for art in articles:
            aid = article_id(art)
            if aid in seen_ids:
                continue
            seen_ids.add(aid)

            art["relevance_score"] = compute_relevance(art, cat_cfg["keywords"])
            if art["relevance_score"] < 20:
                continue

            art["edge"] = estimate_edge(art, cat_name)
            art["category"] = cat_name
            art["related_markets"] = cat_cfg["kalshi_markets"]
            art["id"] = aid
            art["crawled_at"] = datetime.now(timezone.utc).isoformat()
            all_signals.append(art)

        cat_signals = [a for a in all_signals if a.get("category") == cat_name]
        print(f"  Found {len(cat_signals)} relevant signals")

    # Sort by relevance
    all_signals.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    # ---------- Save JSON ----------
    save_json(SIGNALS_JSON, {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signal_count": len(all_signals),
        "signals": all_signals,
    })
    print(f"\nSaved {len(all_signals)} signals to {SIGNALS_JSON.name}")

    # ---------- Save Markdown ----------
    md_lines = [
        "# Kalshi News Signals",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total signals: {len(all_signals)}",
        "",
    ]

    # Summary of high/medium edge
    high_edge = [s for s in all_signals if s["edge"] == "HIGH"]
    med_edge = [s for s in all_signals if s["edge"] == "MEDIUM"]
    if high_edge or med_edge:
        md_lines.append("## !! ACTION ITEMS - Potential Mispricings !!")
        md_lines.append("")
        for s in high_edge + med_edge:
            md_lines.append(f"### [{s['edge']}] {s['category']}")
            md_lines.append(f"- **{s['title']}**")
            md_lines.append(f"- Source: {s.get('source', 'N/A')} | Relevance: {s['relevance_score']}/100")
            md_lines.append(f"- Link: {s['link']}")
            md_lines.append(f"- Related markets: {', '.join(s['related_markets'])}")
            md_lines.append("")

    # Full list by category
    md_lines.append("## All Signals by Category")
    md_lines.append("")
    for cat_name in MARKET_CATEGORIES:
        cat_sigs = [s for s in all_signals if s["category"] == cat_name]
        if not cat_sigs:
            continue
        md_lines.append(f"### {cat_name}")
        for s in cat_sigs:
            md_lines.append(f"- [{s['edge']}] (score {s['relevance_score']}) {s['title']}")
            md_lines.append(f"  - {s['link']}")
        md_lines.append("")

    SIGNALS_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Saved markdown report to {SIGNALS_MD.name}")

    # ---------- Update History ----------
    history = load_json(HISTORY_JSON)
    if "runs" not in history:
        history["runs"] = []
    history["runs"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal_count": len(all_signals),
        "high_edge": len(high_edge),
        "medium_edge": len(med_edge),
        "categories_hit": list(set(s["category"] for s in all_signals)),
    })
    # Keep last 100 runs
    history["runs"] = history["runs"][-100:]

    # Track individual signals over time
    if "signal_tracker" not in history:
        history["signal_tracker"] = {}
    for s in all_signals:
        sid = s["id"]
        if sid not in history["signal_tracker"]:
            history["signal_tracker"][sid] = {
                "title": s["title"],
                "category": s["category"],
                "edge": s["edge"],
                "first_seen": s["crawled_at"],
                "relevance_score": s["relevance_score"],
                "times_seen": 0,
            }
        history["signal_tracker"][sid]["times_seen"] += 1
        history["signal_tracker"][sid]["last_seen"] = s["crawled_at"]

    # Prune signals older than 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    history["signal_tracker"] = {
        k: v for k, v in history["signal_tracker"].items()
        if v.get("last_seen", "") >= cutoff
    }

    save_json(HISTORY_JSON, history)
    print(f"Updated signal history ({len(history['signal_tracker'])} tracked signals)")

    # ---------- Summary ----------
    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  Total signals: {len(all_signals)}")
    print(f"  HIGH edge:     {len(high_edge)}")
    print(f"  MEDIUM edge:   {len(med_edge)}")
    if high_edge:
        print("\n  >> HIGH EDGE ALERTS:")
        for s in high_edge[:5]:
            print(f"     [{s['category']}] {s['title'][:80]}")
    print("=" * 60)


if __name__ == "__main__":
    crawl_all()
