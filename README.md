A FastAPI API that scrapes information from albumoftheyear.org.

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
