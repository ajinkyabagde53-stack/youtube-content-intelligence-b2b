"""
YouTube Content Intelligence Agent for B2B SaaS
Step 1: Setup — imports, API config, ICP input
Step 2: YouTube search — query builder + video results fetcher
"""

import os
import requests
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ── ICP Input ────────────────────────────────────────────────────────────────
# Edit these values to match the target company's ideal customer profile

ICP = {
    "job_title": "VP of Marketing",
    "industry": "B2B SaaS",
    "company_size": "50-500 employees",
    "pain_points": [
        "generating qualified pipeline from content",
        "proving ROI of content marketing",
        "standing out on YouTube against bigger brands",
        "converting YouTube viewers into demo requests",
    ],
    "product_category": "RevOps automation for mid-market SaaS",
}

COMPETITOR_CHANNELS = [
    # Add competitor YouTube channel IDs here
    # Example: "UCxxxxxxxxxxxxxxxxxxxxxxxx"
]

# ── Step 2: YouTube Search ────────────────────────────────────────────────────

def build_search_queries(icp):
    """Generate 8-10 search queries from ICP pain points."""
    queries = []
    for pain_point in icp["pain_points"]:
        queries.append(f"{pain_point} B2B SaaS")
        queries.append(f"how to {pain_point}")
    queries.append(f"{icp['product_category']} strategy")
    queries.append(f"B2B YouTube marketing {icp['industry']}")
    return queries[:10]  # cap at 10 queries


def search_youtube(query, api_key, max_results=10):
    """Search YouTube Data API v3 and return top video results."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "relevance",
        "key": api_key,
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"]["description"],
        })
    return results


def fetch_all_search_results(icp, api_key):
    """Run all queries and collect video results."""
    queries = build_search_queries(icp)
    all_results = {}

    for query in queries:
        print(f"🔍 Searching: {query}")
        results = search_youtube(query, api_key)
        all_results[query] = results
        print(f"   Found {len(results)} videos")

    return all_results


if __name__ == "__main__":
    print("✅ Step 1 complete — ICP loaded successfully")
    print(f"Target: {ICP['job_title']} in {ICP['industry']}")
    print(f"Pain points: {len(ICP['pain_points'])} identified\n")

    print("🚀 Step 2 — Running YouTube search...")
    if YOUTUBE_API_KEY and YOUTUBE_API_KEY != "your_youtube_api_key_here":
        results = fetch_all_search_results(ICP, YOUTUBE_API_KEY)
        print(f"\n✅ Step 2 complete — {sum(len(v) for v in results.values())} videos found")
    else:
        print("⚠️  Add your YouTube API key to .env to run search")
