"""
YouTube Content Intelligence Agent for B2B SaaS
Step 1: Setup — imports, API config, ICP input
Step 2: YouTube search — query builder + video results fetcher
Step 3: Transcript fetcher — pull transcripts from competitor videos
Step 4: Claude AI analysis — extract patterns, hooks, and gaps from transcripts
Step 5: Brief generator — produce a ready-to-film video brief from the analysis
"""

import os
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import anthropic

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


# ── Step 4: Claude AI Analysis ───────────────────────────────────────────────

def analyze_transcript_with_claude(transcript, title, api_key):
    """
    Send a transcript to Claude and extract:
    - Core argument
    - Hook structure (first 30 seconds)
    - Keywords used
    - Content gaps or weaknesses
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a B2B content strategist analyzing a YouTube video transcript.

Video title: {title}

Transcript:
{transcript[:4000]}

Analyze this transcript and return a structured response with exactly these sections:

CORE ARGUMENT: (one sentence — what is the main point of this video?)
HOOK STRUCTURE: (how does the video open? what problem does it hook on?)
KEYWORDS USED: (list the 5-8 most important keywords/phrases)
CONTENT GAPS: (what important angles, data, or insights did this video miss?)
AUDIENCE FIT: (is this content aimed at the right B2B buyer, or too broad?)
"""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def analyze_all_transcripts(transcripts, api_key):
    """Run Claude analysis on all fetched transcripts."""
    analyses = {}

    for video_id, data in transcripts.items():
        print(f"\n🤖 Analyzing: {data['title'][:60]}...")
        analysis = analyze_transcript_with_claude(
            data["transcript"], data["title"], api_key
        )
        analyses[video_id] = {
            "title": data["title"],
            "channel": data["channel"],
            "analysis": analysis,
        }
        print("   ✅ Done")

    return analyses


# ── Step 5: Video Brief Generator ────────────────────────────────────────────

def generate_video_brief(icp, analyses, api_key):
    """
    Uses Claude to synthesize all analyses into one
    ready-to-film video brief for the highest-opportunity topic.
    """
    client = anthropic.Anthropic(api_key=api_key)

    # Combine all analyses into one context block
    combined = ""
    for video_id, data in analyses.items():
        combined += f"\n\nVideo: {data['title']}\nChannel: {data['channel']}\n{data['analysis']}"

    prompt = f"""You are a B2B YouTube strategist. Based on competitor video analyses below,
generate a complete video brief for a B2B SaaS company targeting this ICP:

Job Title: {icp['job_title']}
Industry: {icp['industry']}
Company Size: {icp['company_size']}
Pain Points: {', '.join(icp['pain_points'])}
Product Category: {icp['product_category']}

COMPETITOR ANALYSES:
{combined[:6000]}

Generate a complete video brief with exactly these sections:

TOPIC: (the specific video topic — high demand, not well covered by competitors)
SEO TITLE: (search-intent phrased, under 60 characters)
ALGORITHM TITLE: (curiosity/browse optimised alternative)
HOOK (first 30 seconds): (specific problem statement that makes the ICP stop scrolling)
OUTLINE:
  Point 1:
  Point 2:
  Point 3:
  Point 4:
  Point 5:
PROOF POINTS: (data, case studies, or examples to include)
THUMBNAIL DIRECTION: (face expression + text overlay + background color)
CTA: (call to action matched to buyer journey stage)
WHAT NOT TO DO: (mistakes competitors make on this topic)
"""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def save_brief(brief, icp):
    """Save the generated brief to a markdown file."""
    filename = f"brief_{icp['job_title'].replace(' ', '_').lower()}.md"
    with open(filename, "w") as f:
        f.write(f"# Video Brief — {icp['job_title']} in {icp['industry']}\n\n")
        f.write(brief)
    print(f"\n💾 Brief saved to: {filename}")
    return filename


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

        print("\n🚀 Step 4 — Analyzing transcripts with Claude...")
        if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
            analyses = analyze_all_transcripts(transcripts, ANTHROPIC_API_KEY)
            print(f"\n✅ Step 4 complete — {len(analyses)} videos analyzed")

            print("\n🚀 Step 5 — Generating video brief...")
            brief = generate_video_brief(ICP, analyses, ANTHROPIC_API_KEY)
            save_brief(brief, ICP)
            print("\n✅ All steps complete — your video brief is ready!")
            print("\n" + "="*60)
            print(brief)
        else:
            print("⚠️  Add your Anthropic API key to .env to run analysis")
    else:
        print("⚠️  Add your YouTube API key to .env to run search")
