"""
YouTube Content Intelligence Agent for B2B SaaS
Step 1: Setup — imports, API config, ICP input
"""

import os
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

if __name__ == "__main__":
    print("✅ Step 1 complete — ICP loaded successfully")
    print(f"Target: {ICP['job_title']} in {ICP['industry']}")
    print(f"Pain points: {len(ICP['pain_points'])} identified")
