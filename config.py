import os
from dotenv import load_dotenv

load_dotenv()

# Optional API Keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "NicheRadarApp/1.0")

# Intent Signal Keywords
HIGH_INTENT_KEYWORDS = [
    "looking for", "recommendation", "recommend", "need a", "who is the best",
    "hiring", "hire", "suggest", "any good", "seeking", "quote", "cost of", "best"
]

MEDIUM_INTENT_KEYWORDS = [
    "how to find", "experience with", "review", "thoughts on", "advice",
    "opinion", "where to get", "options for"
]

# User-Agent rotation for standard web fetching
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

# Platform site domain map for SERP search
PLATFORM_DOMAINS = {
    "Reddit": "site:reddit.com",
    "LinkedIn": "site:linkedin.com",
    "Quora": "site:quora.com",
    "Twitter / X": "site:x.com",
    "Web Forums": "forum"
}
