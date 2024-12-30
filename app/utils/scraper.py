import cloudscraper
import urllib.parse
import asyncio

from bs4 import BeautifulSoup
from typing import Optional, Final
from ..models import Album, Track, CriticReview, UserReview
from fastapi import HTTPException

BASE_URL: Final = "https://www.albumoftheyear.org"
HEADERS: Final = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}

scraper = cloudscraper.create_scraper()


async def get_album_url(artist: str, album: str) -> Optional[tuple[str, str, str]]:
    """
    Search for an album.
    """
    search_query = urllib.parse.quote(f"{artist} {album}")
    url = f"{BASE_URL}/search/albums/?q={search_query}"

    try:
        response_text = await asyncio.to_thread(
            lambda: scraper.get(url, headers=HEADERS).text
        )

        soup = BeautifulSoup(response_text, "html.parser")

        if album_block := soup.select_one(".albumBlock"):
            if album_link := album_block.select_one(".image a"):
                return (
                    f"{BASE_URL}{album_link['href']}",
                    album_block.select_one(".artistTitle").text.strip(),
                    album_block.select_one(".albumTitle").text.strip(),
                )
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Error accessing album site: {str(e)}"
        )

    return None


def parse_tracks(soup: BeautifulSoup) -> list[Track]:
    """Extract track information from the album page."""
    tracks = []
    for row in soup.select(".trackListTable tr"):
        number = int(row.select_one(".trackNumber").text)
        title = row.select_one(".trackTitle a").text
        length = row.select_one(".length").text if row.select_one(".length") else ""
        rating = None

        if rating_elem := row.select_one(".trackRating span"):
            rating = int(rating_elem.text)

        featured_artists = []
        if featured_elem := row.select_one(".featuredArtists"):
            featured_artists = [a.text for a in featured_elem.select("a")]

        tracks.append(
            Track(
                number=number,
                title=title,
                length=length,
                rating=rating,
                featured_artists=featured_artists,
            )
        )

    return tracks


def parse_critic_reviews(soup: BeautifulSoup) -> list[CriticReview]:
    """Extract critic reviews from the album page."""
    reviews = []
    for review in soup.select("#critics .albumReviewRow"):
        author = (
            review.select_one(".author a").text
            if review.select_one(".author a")
            else "Unknown"
        )
        publication = review.select_one(".publication a").text
        rating_text = review.select_one(".albumReviewRating").text
        rating = int(rating_text) if rating_text.isdigit() else 0
        text = review.select_one(".albumReviewText").text.strip()

        reviews.append(
            CriticReview(
                author=author,
                publication=publication,
                rating=rating,
                text=text,
            )
        )

    return reviews


def parse_user_reviews(soup: BeautifulSoup, section_id: str) -> list[UserReview]:
    """Extract user reviews from the album page."""
    reviews = []
    for review in soup.select(f"#{section_id} .albumReviewRow"):
        author = review.select_one(".userReviewName a").text
        rating = None

        if rating_elem := review.select_one(".rating"):
            if rating_elem.text != "NR":
                rating = int(rating_elem.text)

        text = review.select_one(".albumReviewText").text.strip()
        likes = 0

        if likes_elem := review.select_one(".review_likes a"):
            likes = int(likes_elem.text)

        reviews.append(
            UserReview(
                author=author,
                rating=rating,
                text=text,
                likes=likes,
            )
        )

    return reviews


async def scrape_album(url: str, artist: str, title: str) -> Album:
    """
    Scrape detailed album information from albumoftheyear.org.
    """
    try:
        response_text = await asyncio.to_thread(
            lambda: scraper.get(url, headers=HEADERS).text
        )

        soup = BeautifulSoup(response_text, "html.parser")

        user_score = None
        if score_elem := soup.select_one(".albumUserScore a"):
            try:
                user_score = float(score_elem.get("title", 0))
            except (ValueError, TypeError):
                pass

        num_ratings = 0
        if ratings_elem := soup.select_one(".numReviews strong"):
            try:
                num_ratings = int(ratings_elem.text)
            except ValueError:
                pass

        tracks_task = asyncio.create_task(asyncio.to_thread(parse_tracks, soup))
        critic_reviews_task = asyncio.create_task(
            asyncio.to_thread(parse_critic_reviews, soup)
        )
        popular_reviews_task = asyncio.create_task(
            asyncio.to_thread(parse_user_reviews, soup, "users")
        )

        # wait for all parsing tasks to complete
        tracks, critic_reviews, popular_reviews = await asyncio.gather(
            tracks_task,
            critic_reviews_task,
            popular_reviews_task,
        )

        return Album(
            title=title,
            artist=artist,
            user_score=user_score,
            num_ratings=num_ratings,
            tracks=tracks,
            critic_reviews=critic_reviews,
            popular_reviews=popular_reviews,
            is_must_hear=bool(soup.select_one(".mustHearButton")),
        )

    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Error accessing album page: {str(e)}"
        )
