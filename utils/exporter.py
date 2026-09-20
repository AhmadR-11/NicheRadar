import pandas as pd
from typing import List
from fetchers.base import PostItem

def posts_to_dataframe(posts: List[PostItem]) -> pd.DataFrame:
    """Converts a list of PostItem models into a display-ready Pandas DataFrame."""
    if not posts:
        return pd.DataFrame()
    
    data = []
    for p in posts:
        data.append({
            "Platform": p.platform,
            "Intent Signal": p.intent_score,
            "Title": p.title,
            "Post Link": p.url,
            "Snippet": p.snippet[:150] + "..." if len(p.snippet) > 150 else p.snippet,
            "Matched Keywords": ", ".join(p.matched_keywords) if p.matched_keywords else "N/A",
            "Published Date": p.published_date,
            "Location": p.location or "",
            "Niche": p.niche or ""
        })
    return pd.DataFrame(data)

def export_to_csv(posts: List[PostItem]) -> str:
    df = posts_to_dataframe(posts)
    return df.to_csv(index=False)
