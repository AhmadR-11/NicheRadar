from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PostItem(BaseModel):
    title: str = Field(..., description="Title of the social media post or discussion thread")
    url: str = Field(..., description="Direct link to the post")
    platform: str = Field(..., description="Social platform name (Reddit, LinkedIn, Quora, etc.)")
    snippet: str = Field(default="", description="Body text excerpt or search result snippet")
    published_date: Optional[str] = Field(default="Recent", description="Publication date string or timestamp")
    intent_score: str = Field(default="Medium Intent", description="Calculated intent level: High Intent, Medium Intent, Low Intent")
    matched_keywords: list[str] = Field(default_factory=list, description="Keywords triggered in intent analysis")
    author: Optional[str] = Field(default=None, description="Post author or community name")
    location: Optional[str] = Field(default=None, description="Location context matched")
    niche: Optional[str] = Field(default=None, description="Niche category matched")
