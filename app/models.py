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


class AlbumUserReview(BaseModel):
    author: str
    rating: Optional[int] = None
    text: str
    likes: int = 0


class ProfileUserReview(BaseModel):
    album_title: str
    album_artist: str
    rating: int
    review_text: str
    likes: int
    timestamp: str


class BuyLink(BaseModel):
    platform: str
    url: str


class Album(BaseModel):
    title: str
    artist: str
    user_score: Optional[float]
    num_ratings: int
    tracks: List[Track]
    critic_reviews: List[CriticReview]
    popular_reviews: List[AlbumUserReview]
    is_must_hear: bool
    buy_links: List[BuyLink] = []


class UserProfile(BaseModel):
    username: str
    location: Optional[str] = None
    about: Optional[str] = None
    member_since: Optional[str] = None
    stats: dict
    favorite_albums: List[str]
    recent_reviews: List[ProfileUserReview]
    social_links: Optional[dict] = None
    rating_distribution: dict
