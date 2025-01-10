A FastAPI API that scrapes information from albumoftheyear.org.

[![Live Instance](https://img.shields.io/badge/Live_Instance-aoty.jawad.sh-blue)](https://aoty.jawad.sh/)
[![Swagger Docs](https://img.shields.io/badge/Swagger_Docs-aoty.jawad.sh/docs-blue)](https://aoty.jawad.sh/docs)

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
