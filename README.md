A FastAPI API that scrapes information from albumoftheyear.org.

[![Live Instance](https://img.shields.io/badge/Live_Instance-aoty.jawad.sh-blue)](https://aoty.jawad.sh/)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Example Responses](#example-responses)

## Installation

1. Create a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
uv pip install -r requirements.txt
```

## Usage

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Get Album Details

```http
GET /album/?artist={artist}&album={album}
```

Retrieves detailed information about a specific album.

### Get User Profile

```http
GET /user/?username={username}
```

Retrieves detailed information about a user profile.

### View Metrics

```http
GET /metrics
```

Returns API metrics.

## Example Responses

### Album Details Response

```http
GET /album/?artist=radiohead&album=ok+computer
```

```json
{
  "title": "OK Computer",
  "artist": "Radiohead",
  "user_score": 93.4,
  "num_ratings": 13,
  "tracks": [
    {
      "number": 1,
      "title": "Airbag",
      "length": "4:47",
      "rating": 94,
      "featured_artists": []
    },
    "..."
  ],
  "critic_reviews": [
    {
      "author": "Ryan Schreiber",
      "publication": "Pitchfork",
      "rating": 100,
      "text": "The record is brimming with genuine emotion, beautiful and complex imagery and music, and lyrics that are at ..."
    },
    "..."
  ],
  "popular_reviews": [
    {
      "author": "RandomChUllz",
      "rating": 100,
      "text": "We are living what this album feared right now.",
      "likes": 0
    },
    "..."
  ],
  "is_must_hear": true
}
```

### User Profile Response

```http
GET /user/?username=fantano
```

```json
{
  "username": "andre...",
  "location": "Italy",
  "about": "I simply like good music, the genre doesn't matter.",
  "member_since": "August 11, 2017",
  "stats": {
    "ratings": 2613,
    "reviews": 11,
    "lists": 0,
    "followers": 2845
  },
  "favorite_albums": [
    "OK Computer",
    "Revolver",
    "The Velvet Underground & Nico",
    "Disintegration",
    "The Rise and Fall of Ziggy Stardust and the Spiders from Mars"
  ],
  "recent_reviews": [
    {
      "album_title": "Is This It",
      "album_artist": "The Strokes",
      "rating": 91,
      "review_text": "I just realized that I have 2,500 followers in AOTY! Tis is such an honor that I ...",
      "likes": 83,
      "timestamp": "1y"
    },
    "..."
  ],
  "social_links": {
    "link": "https://arock.rocks/",
    "twitter": "http://twitter.com/..."
  },
  "rating_distribution": {
    "100": 16,
    "90-99": 232,
    "80-89": 1019,
    "70-79": 1085,
    "60-69": 219,
    "50-59": 26,
    "40-49": 12
  }
}
```

### Metrics Response

```http
GET /metrics
```

```json
{
  "total_requests": 7,
  "cache_hits": 5,
  "cache_misses": 2,
  "errors": 0,
  "avg_response_time": 0.158826896122524,
  "last_reset": "2024-12-30T05:17:38.585115"
}
```
