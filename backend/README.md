# Financial AI Backend (FastAPI)

FastAPI backend for Financial AI with RAG-powered financial planning.

## Features

- FastAPI REST API
- RAG (Retrieval-Augmented Generation) using TF-IDF + Cosine Similarity
- OpenAI GPT-4o integration
- Financial playbook grounding from markdown

## Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=3001
```

### 4. Run the Server

```bash
# Development mode (with auto-reload)
python main.py

# OR using uvicorn directly
uvicorn main:app --reload --port 3001
```

The API will be available at `http://localhost:3001`

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://localhost:3001/docs`
- ReDoc: `http://localhost:3001/redoc`

## API Endpoints

### POST `/api/generate-plan`

Generate a personalized financial plan.

**Request Body:**
```json
{
  "aboutYou": "Professional",
  "income": "60,001–100,000",
  "expenses": "2,501–4,000",
  "debt": "Student loan",
  "savings": "10k–50k",
  "riskTolerance": "Medium"
}
```

**Response:**
```json
{
  "situation": "...",
  "priorities": ["...", "...", "..."],
  "roadmap": "...",
  "thisMonthActions": "...",
  "longTermStrategy": "..."
}
```

### POST `/api/refine-plan`

Refine plan through AI chat.

**Request Body:**
```json
{
  "message": "How can I save more money?",
  "planData": { ... },
  "chatHistory": [ ... ]
}
```

### GET `/api/health`

Health check endpoint.

## RAG Implementation

The RAG system uses:
- **TF-IDF Vectorization** for semantic search
- **Cosine Similarity** for relevance scoring
- **Keyword Matching** for additional relevance
- **Hybrid Scoring**: 70% semantic similarity + 30% keyword relevance

The financial playbook is chunked into 1500-character segments with 300-character overlap for optimal context retrieval.

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── services/
│   ├── rag_service.py     # RAG implementation
│   └── openai_service.py  # OpenAI integration
├── data/
│   └── financial-playbook.md  # Financial guidance document
├── requirements.txt
└── .env
```
