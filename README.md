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
    ...
  ],
  "critic_reviews": [
    {
      "author": "Ryan Schreiber",
      "publication": "Pitchfork",
      "rating": 100,
      "text": "The record is brimming with genuine emotion, beautiful and complex imagery and music, and lyrics that are at ..."
    },
    ...
  ],
  "popular_reviews": [
    {
      "author": "RandomChUllz",
      "rating": 100,
      "text": "We are living what this album feared right now.",
      "likes": 0
    },
    ...
  ],
  "is_must_hear": true
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
