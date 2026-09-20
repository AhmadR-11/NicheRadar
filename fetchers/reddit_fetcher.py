import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
import urllib.parse
from fetchers.base import PostItem
from utils.intent_analyzer import analyze_intent

def fetch_reddit_posts(
    niche: str, 
    location: str, 
    limit: int = 15, 
    time_filter: str = "Past 24 Hours",
    lead_focus: str = "Questioning & Recommendations ❓",
    custom_keywords: str = ""
) -> List[PostItem]:
    """
    Fetches real-time posts from Reddit matching niche, location, intent focus, and custom keywords.
    """
    time_map = {
        "Past 24 Hours": "day",
        "Past Week": "week",
        "Past Month": "month",
        "Past Year": "year",
        "Anytime": "all"
    }
    t_val = time_map.get(time_filter, "day")
    
    # Build intent modifier based on Lead Focus mode
    intent_terms = ""
    if "Questioning" in lead_focus:
        intent_terms = "looking for OR recommendation OR best OR suggest OR need"
    elif "Hiring" in lead_focus:
        intent_terms = "hiring OR job OR vacancy"
        
    if custom_keywords.strip():
        intent_terms = f"{intent_terms} {custom_keywords.strip()}".strip()
        
    query = f"{niche} {location} {intent_terms}".strip()
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=new&t={t_val}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NicheRadar/1.0"
    }
    
    posts = []
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = client.get(rss_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "xml")
                entries = soup.find_all("entry")
                
                for entry in entries[:limit]:
                    title_elem = entry.find("title")
                    link_elem = entry.find("link")
                    content_elem = entry.find("content")
                    updated_elem = entry.find("updated")
                    author_elem = entry.find("author")
                    
                    title = title_elem.get_text(strip=True) if title_elem else "Reddit Discussion"
                    url = link_elem["href"] if link_elem and "href" in link_elem.attrs else ""
                    
                    # Ignore main subreddit pages (only include post comments)
                    if "/comments/" not in url:
                        continue
                        
                    snippet = ""
                    if content_elem:
                        content_bs = BeautifulSoup(content_elem.get_text(), "html.parser")
                        snippet = content_bs.get_text(strip=True)[:250]
                        
                    date_str = "Recent"
                    if updated_elem:
                        date_str = updated_elem.get_text(strip=True).replace("T", " ")[:16]
                        
                    author_name = "u/anonymous"
                    if author_elem and author_elem.find("name"):
                        author_name = author_elem.find("name").get_text(strip=True)
                        
                    intent_score, keywords = analyze_intent(title, snippet)
                    
                    posts.append(PostItem(
                        title=title,
                        url=url,
                        platform="Reddit",
                        snippet=snippet if snippet else f"Reddit discussion for {niche} in {location}",
                        published_date=date_str,
                        intent_score=intent_score,
                        matched_keywords=keywords,
                        author=author_name,
                        location=location,
                        niche=niche
                    ))
    except Exception as e:
        print(f"[Reddit Fetcher] Error fetching Reddit posts: {e}")
        
    return posts
