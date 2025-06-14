from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Episode(BaseModel):
    episode_id: int
    title: str
    duration: str
    aired: Optional[str] = None
    synopsis: Optional[str] = None

class AnimeBase(BaseModel):
    mal_id: int
    title: str
    title_english: Optional[str] = None
    title_japanese: Optional[str] = None
    synopsis: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    aired_from: Optional[str] = None
    aired_to: Optional[str] = None
    rating: Optional[str] = None
    score: Optional[float] = None
    genres: List[str] = []
    studios: List[str] = []
    year: Optional[int] = None
    season: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    duration: Optional[str] = None
    image_url: Optional[str] = None
    trailer_url: Optional[str] = None

class Anime(AnimeBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    episodes_list: List[Episode] = []
    view_count: int = 0
    like_count: int = 0

class AnimeCreate(AnimeBase):
    pass

class AnimeUpdate(BaseModel):
    title: Optional[str] = None
    synopsis: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    score: Optional[float] = None
    genres: Optional[List[str]] = None
    studios: Optional[List[str]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    anime_id: str
    user_name: str = "Анонимный пользователь"
    text: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    likes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentCreate(BaseModel):
    anime_id: str
    text: str
    rating: Optional[int] = Field(None, ge=1, le=5)

class SearchQuery(BaseModel):
    query: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    rating: Optional[str] = None
    score_min: Optional[float] = None
    score_max: Optional[float] = None
    limit: int = Field(default=20, le=50)
    page: int = Field(default=1, ge=1)