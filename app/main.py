import asyncio

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from time import time
from contextlib import asynccontextmanager
from .utils.cache import cache
from .models import Album, UserProfile
from .utils.metrics import metrics
from .utils.scraper import get_album_url, scrape_album, get_user_profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AOTY API",
    description="An API that scrapes album and user information from albumoftheyear.org.",
    version="1.0.0",
    contact={
        "name": "spkrbox",
        "url": "https://github.com/spkrbox/albumoftheyear-api",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rate limit error handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"detail": f"Internal server error: {str(exc)}"}
    )


@app.get("/")
async def home():
    return {
        "endpoints": {
            "album": {
                "path": "/album/",
                "params": {"artist": "string", "album": "string"},
                "description": "Get detailed album information",
            },
            "metrics": {"path": "/metrics", "description": "Get API usage metrics"},
            "user": {
                "path": "/user/",
                "params": {"username": "string"},
                "description": "Get user profile information",
            },
        },
    }


@app.get(
    "/album/",
    response_model=Album,
    summary="Get Album Details",
    response_description="Detailed album information including tracks, reviews and ratings",
    responses={
        404: {"description": "Album not found"},
        503: {"description": "Error accessing album site"},
    },
)
@limiter.limit("30/minute")
async def get_album(
    request: Request,
    artist: str = Query(..., description="Name of the artist", example="Radiohead"),
    album: str = Query(..., description="Name of the album", example="OK Computer"),
):
    """
    Fetches detailed information about an album from albumoftheyear.org

    The endpoint will:
    - Search for the album
    - Scrape track listings, user score, and reviews
    - Return cached results if available

    Rate limited to 30 requests per minute per IP address.
    """
    start_time = time()
    try:
        cache_key = f"{artist}:{album}"
        if cached_result := cache.get(cache_key):
            metrics.record_request(cache_hit=True)
            return cached_result

        metrics.record_request(cache_hit=False)
        result = await get_album_url(artist, album)
        if not result:
            raise HTTPException(status_code=404, detail="Album not found")

        album_url, artist_name, album_title = result

        async with asyncio.Semaphore(5):
            album_data = await scrape_album(album_url, artist_name, album_title)

        cache.set(cache_key, album_data)
        return album_data

    except:
        metrics.record_error()
        raise
    finally:
        metrics.record_response_time(time() - start_time)


@app.get(
    "/metrics",
    summary="API Usage Metrics",
    response_description="Current API usage statistics",
    responses={
        200: {
            "description": "API metrics including request counts and response times",
            "content": {
                "application/json": {
                    "example": {
                        "total_requests": 7,
                        "cache_hits": 5,
                        "cache_misses": 2,
                        "errors": 0,
                        "avg_response_time": 0.158826896122524,
                        "last_reset": "2024-12-30T05:17:38.585115",
                    }
                }
            },
        }
    },
)
async def get_metrics():
    """
    Returns current API usage metrics including:
    - Total request count
    - Cache hit/miss statistics
    - Error count
    - Average response time
    - Last metrics reset timestamp
    """
    return metrics.get_metrics()


@app.get(
    "/user/",
    response_model=UserProfile,
    summary="Get User Profile",
    response_description="User profile information including reviews and stats",
    responses={
        404: {"description": "User not found"},
        503: {"description": "Error accessing user profile"},
    },
)
@limiter.limit("30/minute")
async def get_user(
    request: Request,
    username: str = Query(
        ..., description="Username on albumoftheyear.org", example="fantano"
    ),
):
    """
    Fetches a user's profile information from albumoftheyear.org

    The endpoint will return:
    - Basic profile information (location, join date, etc.)
    - User statistics (ratings, reviews, followers)
    - Recent reviews
    - Favorite albums
    - Rating distribution
    - Social media links

    Rate limited to 30 requests per minute per IP address.
    """
    start_time = time()
    try:
        cache_key = f"user_{username}"
        if cached_result := cache.get(cache_key):
            metrics.record_request(cache_hit=True)
            return cached_result

        metrics.record_request(cache_hit=False)
        if user_data := await get_user_profile(username):
            cache.set(cache_key, user_data)
            return user_data

        raise HTTPException(status_code=404, detail="User not found")

    except:
        metrics.record_error()
        raise
    finally:
        metrics.record_response_time(time() - start_time)
