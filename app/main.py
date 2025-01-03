import asyncio

from fastapi import FastAPI, HTTPException, Request
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


app = FastAPI(title="AOTY Scraper", lifespan=lifespan)
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
        },
    }


@app.get("/album/", response_model=Album)
@limiter.limit("30/minute")
async def get_album(request: Request, artist: str, album: str):
    """
    Search for and scrape album information from albumoftheyear.org

    Parameters:
    - artist: Name of the artist
    - album: Name of the album

    Returns:
    - Album object containing all scraped information
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


@app.get("/metrics")
async def get_metrics():
    """Get API usage metrics."""
    return metrics.get_metrics()


@app.get("/user/", response_model=UserProfile)
@limiter.limit("30/minute")
async def get_user(request: Request, username: str):
    """Get user profile information"""
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
