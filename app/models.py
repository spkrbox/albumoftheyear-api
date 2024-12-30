from pydantic import BaseModel
from typing import Optional, List


class Track(BaseModel):
    number: int
    title: str
    length: str
    rating: Optional[int] = None
    featured_artists: List[str] = []


class CriticReview(BaseModel):
    author: str
    publication: str
    rating: int
    text: str


class UserReview(BaseModel):
    author: str
    rating: Optional[int]
    text: str
    likes: int


class Album(BaseModel):
    title: str
    artist: str
    user_score: Optional[float]
    num_ratings: int
    tracks: List[Track]
    critic_reviews: List[CriticReview]
    popular_reviews: List[UserReview]
    is_must_hear: bool
