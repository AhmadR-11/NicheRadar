import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
import urllib.parse
import re
import time
from fetchers.base import PostItem
from utils.intent_analyzer import analyze_intent
from config import SERPER_API_KEY
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

def is_valid_post_link(url: str, platform: str) -> bool:
    """Strictly validates that the extracted URL is a direct post/thread link."""
    u = url.lower()
    if platform == "LinkedIn":
        is_post = any(k in u for k in ["/posts/", "/pulse/", "/feed/update/", "search/results/content"])
        is_excluded = any(k in u for k in ["/jobs/", "/company/", "/services/", "/directory/"])
        return is_post and not is_excluded
    elif platform == "Reddit":
        return "/comments/" in u
    elif platform == "Quora":
        is_quora = "quora.com/" in u or "/answer/" in u
        is_excluded = any(k in u for k in ["/press", "/about", "/contact", "q.quora.com", "/careers"])
        return is_quora and not is_excluded
    elif platform == "Twitter / X":
        return "/status/" in u
    elif platform == "Web Forums":
        return any(k in u for k in ["/thread", "/topic", "/discussion", "/viewtopic", "post"])
    return True

def fetch_serp_posts(
    platform_name: str, 
    niche: str, 
    location: str, 
    limit: int = 10, 
    time_filter: str = "Past 24 Hours",
    lead_focus: str = "Questioning & Recommendations ❓",
    custom_keywords: str = ""
) -> List[PostItem]:
    """
    Fetches direct post links from target platforms (LinkedIn, Quora, Twitter/X, Forums)
    using DDGS engine or Serper.dev API if key is available.
    """
    if SERPER_API_KEY:
        site_query = _get_platform_site_query(platform_name)
        full_query = f"{site_query} \"{niche}\" \"{location}\"".strip()
        return _fetch_serper_api(platform_name, full_query, niche, location, limit, time_filter)
    else:
        return _fetch_ddgs_engine(platform_name, niche, location, limit, time_filter, lead_focus, custom_keywords)

def _get_platform_site_query(platform: str) -> str:
    mapping = {
        "LinkedIn": "site:linkedin.com/posts OR site:linkedin.com/pulse",
        "Quora": "site:quora.com",
        "Twitter / X": "site:x.com/*/status OR site:twitter.com/*/status",
        "Reddit": "site:reddit.com/r/*/comments",
        "Web Forums": "inurl:forum OR inurl:thread"
    }
    return mapping.get(platform, "")

def _fetch_ddgs_engine(
    platform: str, 
    niche: str, 
    location: str, 
    limit: int, 
    time_filter: str,
    lead_focus: str,
    custom_keywords: str
) -> List[PostItem]:
    """Primary fetcher engine using TLS impersonated DDGS search targeted specifically at posts & inquiry terms."""
    posts = []
    
    time_map = {
        "Past 24 Hours": "d",
        "Past Week": "w",
        "Past Month": "m",
        "Anytime": None
    }
    t_limit = time_map.get(time_filter, "d")
    
    # Build intent modifier term
    intent_terms = ""
    if "Questioning" in lead_focus:
        intent_terms = "(recommendation OR \"looking for\" OR best OR suggest OR need)"
    elif "Hiring" in lead_focus:
        intent_terms = "(hiring OR job OR vacancy)"
        
    if custom_keywords.strip():
        # Clean custom keywords into OR group
        kw_list = [f'"{k.strip()}"' if ' ' in k.strip() else k.strip() for k in custom_keywords.split(',') if k.strip()]
        if kw_list:
            custom_terms = f"({' OR '.join(kw_list)})"
            intent_terms = f"{intent_terms} {custom_terms}".strip()
            
    # Platform-specific targeted search queries
    if platform == "LinkedIn":
        queries = [
            f"site:linkedin.com/posts \"{niche}\" {location} {intent_terms}".strip(),
            f"site:linkedin.com/posts {niche} {location} \"looking for\"",
            f"site:linkedin.com/posts {niche} {location} recommendation",
            f"\"linkedin.com/posts\" {niche} {location}"
        ]
    elif platform == "Quora":
        queries = [
            f"site:quora.com \"{niche}\" {location} {intent_terms}".strip(),
            f"site:quora.com {niche} {location} recommendation"
        ]
    elif platform == "Twitter / X":
        queries = [
            f"site:x.com {niche} {location} {intent_terms}".strip(),
            f"site:twitter.com {niche} {location} \"looking for\""
        ]
    else:
        queries = [
            f"{platform} {niche} {location} {intent_terms}".strip()
        ]
        
    seen_urls = set()
    
    for q in queries:
        if len(posts) >= limit:
            break
        try:
            results = list(DDGS().text(q, timelimit=t_limit, max_results=limit * 2))
            for r in results:
                if len(posts) >= limit:
                    break
                url = r.get("href", "")
                title = r.get("title", "")
                snippet = r.get("body", "") or r.get("snippet", "")
                
                if not url or url in seen_urls:
                    continue
                    
                # Strictly validate URL is a direct post link
                if not is_valid_post_link(url, platform):
                    continue
                    
                seen_urls.add(url)
                intent_score, keywords = analyze_intent(title, snippet)
                
                posts.append(PostItem(
                    title=title,
                    url=url,
                    platform=platform,
                    snippet=snippet if snippet else f"Post regarding {niche} in {location}",
                    published_date=f"Recent ({time_filter})",
                    intent_score=intent_score,
                    matched_keywords=keywords,
                    location=location,
                    niche=niche
                ))
            time.sleep(0.4)
        except Exception:
            pass
            
    # Direct Fallback Trigger Card
    if not posts:
        encoded_query = urllib.parse.quote(f"{niche} {location} looking for recommendation")
        if platform == "LinkedIn":
            direct_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}"
            title = f"🔥 View Live LinkedIn Questioning & Lead Posts for {niche} in {location}"
            snippet = f"Click to open real-time LinkedIn user recommendations and questions for {niche} in {location} directly on LinkedIn."
        elif platform == "Quora":
            direct_url = f"https://www.quora.com/search?q={encoded_query}"
            title = f"🔥 View Live Quora Questions & Recommendations for {niche} in {location}"
            snippet = f"Click to open live user questions and recommendations for {niche} in {location} directly on Quora."
        elif platform == "Twitter / X":
            direct_url = f"https://x.com/search?q={encoded_query}&f=live"
            title = f"🔥 View Live Tweets for {niche} in {location}"
            snippet = f"Click to view live tweets and updates for {niche} in {location} on Twitter/X."
        else:
            direct_url = f"https://www.google.com/search?q={encoded_query}+forum"
            title = f"🔥 Search Forum Posts for {niche} in {location}"
            snippet = f"Click to browse online forum threads for {niche} in {location}."
            
        posts.append(PostItem(
            title=title,
            url=direct_url,
            platform=platform,
            snippet=snippet,
            published_date=f"Live Feed ({time_filter})",
            intent_score="🔥 High Intent",
            matched_keywords=["Questioning Query"],
            location=location,
            niche=niche
        ))
        
    return posts

def _fetch_serper_api(platform: str, query: str, niche: str, location: str, limit: int, time_filter: str) -> List[PostItem]:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    
    tbs_map = {
        "Past 24 Hours": "qdr:d",
        "Past Week": "qdr:w",
        "Past Month": "qdr:m",
        "Anytime": None
    }
    tbs = tbs_map.get(time_filter)
    payload = {"q": query, "num": limit}
    if tbs:
        payload["tbs"] = tbs
        
    posts = []
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                results = res.json().get("organic", [])
                for item in results:
                    title = item.get("title", "")
                    link = item.get("link", "")
                    snippet = item.get("snippet", "")
                    date_str = item.get("date", f"Recent ({time_filter})")
                    
                    if not is_valid_post_link(link, platform):
                        continue
                        
                    intent_score, keywords = analyze_intent(title, snippet)
                    
                    posts.append(PostItem(
                        title=title,
                        url=link,
                        platform=platform,
                        snippet=snippet,
                        published_date=date_str,
                        intent_score=intent_score,
                        matched_keywords=keywords,
                        location=location,
                        niche=niche
                    ))
    except Exception as e:
        print(f"[Serper API] Error fetching for {platform}: {e}")
    return posts
