import os
import json
import httpx

from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not REDIS_URL or not REDIS_TOKEN:
    raise ValueError(
        "Redis configuration missing. Please set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN"
    )

HEADERS = {"Authorization": f"Bearer {REDIS_TOKEN}"}

# Cache TTLs (in seconds)
ALBUM_TTL = 604800
SIMILAR_TTL = 86400
USER_TTL = 3600


async def set_cache(key: str, value: Any, expire_seconds: int = 3600) -> None:
    """Set a value in Redis cache with expiration"""
    try:
        value_str = json.dumps(value)
        pipeline_data = [["SET", key, value_str], ["EXPIRE", key, str(expire_seconds)]]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{REDIS_URL}/pipeline", headers=HEADERS, json=pipeline_data
            )
            response.raise_for_status()

    except Exception as e:
        print(f"Error setting cache: {str(e)}")


async def get_cache(key: str) -> Optional[Any]:
    """Get a value from Redis cache"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{REDIS_URL}/get/{key}", headers=HEADERS)
            response.raise_for_status()

            data = response.json()
            if data["result"]:
                return json.loads(data["result"])

    except Exception as e:
        print(f"Error getting cache: {str(e)}")

    return None


async def delete_cache(key: str) -> None:
    """Delete a value from Redis cache"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{REDIS_URL}/del/{key}", headers=HEADERS)
            response.raise_for_status()

    except Exception as e:
        print(f"Error deleting cache: {str(e)}")
