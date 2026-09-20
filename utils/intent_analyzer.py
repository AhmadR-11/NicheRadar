from config import HIGH_INTENT_KEYWORDS, MEDIUM_INTENT_KEYWORDS

def analyze_intent(title: str, snippet: str = "") -> tuple[str, list[str]]:
    """
    Analyzes the title and snippet of a post to determine lead intent score.
    Returns a tuple of (Intent Level, List of Matched Keywords).
    """
    combined_text = f"{title} {snippet}".lower()
    matched_high = [kw for kw in HIGH_INTENT_KEYWORDS if kw in combined_text]
    matched_med = [kw for kw in MEDIUM_INTENT_KEYWORDS if kw in combined_text]
    
    if len(matched_high) >= 2 or (len(matched_high) >= 1 and any(q in combined_text for q in ["?", "where", "who", "need", "looking"])):
        return "🔥 High Intent", list(set(matched_high + matched_med))
    elif len(matched_high) >= 1:
        return "🔥 High Intent", matched_high
    elif len(matched_med) >= 1:
        return "⚡ Medium Intent", matched_med
    elif "?" in combined_text:
        return "⚡ Medium Intent", ["Question Format"]
    else:
        return "ℹ️ Low Intent", []
