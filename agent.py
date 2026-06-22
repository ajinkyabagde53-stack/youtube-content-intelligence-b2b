"""
YouTube Content Intelligence Agent for B2B SaaS
Step 1: Setup — imports, API config, ICP input
Step 2: YouTube search — query builder + video results fetcher
Step 3: Transcript fetcher — pull transcripts from competitor videos
"""

import os
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

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


# ── Step 3: Transcript Fetcher ────────────────────────────────────────────────

def fetch_transcript(video_id):
    """Fetch transcript for a single YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Join all text segments into one clean string
        full_text = " ".join([entry["text"] for entry in transcript])
        return full_text
    except Exception as e:
        print(f"   ⚠️  Could not fetch transcript for {video_id}: {e}")
        return None


def fetch_competitor_transcripts(search_results, max_videos=5):
    """
    Pull transcripts from top videos in search results.
    Limits to max_videos per query to stay within API limits.
    """
    transcripts = {}

    for query, videos in search_results.items():
        print(f"\n📄 Fetching transcripts for: {query}")
        for video in videos[:max_videos]:
            video_id = video["video_id"]
            title = video["title"]
            print(f"   → {title[:60]}...")
            text = fetch_transcript(video_id)
            if text:
                transcripts[video_id] = {
                    "title": title,
                    "channel": video["channel"],
                    "transcript": text,
                }

    return transcripts


if __name__ == "__main__":
    print("✅ Step 1 complete — ICP loaded successfully")
    print(f"Target: {ICP['job_title']} in {ICP['industry']}")
    print(f"Pain points: {len(ICP['pain_points'])} identified\n")

    print("🚀 Step 2 — Running YouTube search...")
    if YOUTUBE_API_KEY and YOUTUBE_API_KEY != "your_youtube_api_key_here":
        results = fetch_all_search_results(ICP, YOUTUBE_API_KEY)
        print(f"\n✅ Step 2 complete — {sum(len(v) for v in results.values())} videos found")

        print("\n🚀 Step 3 — Fetching transcripts...")
        transcripts = fetch_competitor_transcripts(results)
        print(f"\n✅ Step 3 complete — {len(transcripts)} transcripts fetched")
    else:
        print("⚠️  Add your YouTube API key to .env to run search")
