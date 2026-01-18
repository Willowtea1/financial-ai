# Financial AI - Personalised Financial Planning Web App

Get your personalised financial plan in 5 minutes using AI. This Vue 3 + FastAPI application helps Malaysian residents create comprehensive financial roadmaps based on their financial situation.

## Features

- 🎯 **Landing Page** - Hero section with clear CTA
- 📋 **Card-Based Questionnaire** - Interactive financial checkup with 6 sections
- 🤖 **AI-Powered Plan Generation** - Uses OpenAI with RAG (Retrieval-Augmented Generation)
- 📊 **Financial Planning Report** - Comprehensive plan with situation, priorities, roadmap, and strategies
- 💬 **AI Refinement Chat** - Interactive chat modal to refine your plan with AI assistance

## Tech Stack

- **Frontend**: Vue 3, Vuetify 3, Vite, Vue Router
- **Backend**: FastAPI (Python)
- **AI**: OpenAI API (GPT-4o)
- **RAG**: TF-IDF + Cosine Similarity for semantic search on markdown playbook

## Project Structure

```
financial-gps/
├── frontend/                 # Vue 3 frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Questionnaire.vue      # Card-based questionnaire component
│   │   │   └── ChatModal.vue          # AI refinement chat modal
│   │   ├── views/
│   │   │   ├── LandingPage.vue        # Landing page with hero section
│   │   │   ├── Questionnaire.vue      # Questionnaire route view
│   │   │   └── FinancialPlan.vue      # Financial plan report page
│   │   ├── router/
│   │   │   └── index.js               # Vue Router configuration
│   │   ├── plugins/
│   │   │   └── vuetify.js             # Vuetify plugin setup
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── backend/                  # FastAPI Python backend
│   ├── services/
│   │   ├── openai_service.py       # OpenAI API integration
│   │   └── rag_service.py          # RAG/grounding service (TF-IDF + Cosine Similarity)
│   ├── data/
│   │   └── financial-playbook.md  # Financial guidance document
│   ├── main.py                   # FastAPI server entry point
│   ├── requirements.txt
│   └── .env.example
├── package.json              # Root package.json with workspace scripts
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

- **Node.js 18+** and npm (for frontend)
- **Python 3.9+** (for backend)
- **OpenAI API key**

### Installation

1. **Clone or navigate to the project directory**

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Set up Python virtual environment and install backend dependencies**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

4. **Set up backend environment variables**
   ```bash
   # Copy the example file and edit it
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=3001
   ```

5. **Start the development servers**

   **Terminal 1 - Frontend (Vue App)**:
   ```bash
   cd frontend
   npm run dev
   ```
   This starts Vite dev server on `http://localhost:5173`

   **Terminal 2 - Backend (FastAPI)**:
   ```bash
   cd backend
   # Make sure venv is activated
   python main.py
   # OR: uvicorn main:app --reload --port 3001
   ```
   This starts FastAPI server on `http://localhost:3001`

6. **Open your browser**
   Navigate to `http://localhost:5173`

## Usage

1. **Landing Page**: Click "Start My Financial Plan" to begin
2. **Questionnaire**: Select options for each financial category:
   - About You
   - Annual Income (RM)
   - Monthly Expenses (RM)
   - Debt
   - Savings
   - Risk Tolerance
3. **Generate Plan**: Click "Generate My Financial Plan" once all sections are complete
4. **View Report**: Review your personalised financial plan
5. **Refine Plan**: Click "Refine My Plan with AI" to chat with AI and refine your plan

## API Endpoints

### POST `/api/generate-plan`
Generates a financial plan based on user questionnaire responses.

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
Refines plan through AI chat interaction.

**Request Body:**
```json
{
  "message": "How can I save more money?",
  "planData": { ... },
  "chatHistory": [ ... ]
}
```

**Response:**
```json
{
  "message": "...",
  "updatedPlan": { ... } // Optional, if plan was updated
}
```

### GET `/api/health`
Health check endpoint.

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:3001/docs`
- **ReDoc**: `http://localhost:3001/redoc`

## RAG System

The app uses a hybrid RAG (Retrieval-Augmented Generation) system:

1. **Financial Playbook**: Located in `backend/data/financial-playbook.md`
2. **Chunking**: Playbook is split into text chunks (1500 chars, 300 overlap) with sentence boundary awareness
3. **TF-IDF Vectorization**: Creates semantic embeddings for all chunks
4. **Cosine Similarity**: Calculates semantic similarity between user query and chunks
5. **Keyword Matching**: Additional relevance scoring based on user answers
6. **Hybrid Scoring**: 70% semantic similarity + 30% keyword relevance
7. **Context Retrieval**: Top 5 relevant chunks are retrieved and passed to OpenAI

You can customize the playbook by editing `backend/data/financial-playbook.md`.

## Customization

### Update Financial Playbook
Edit `backend/data/financial-playbook.md` to customize financial guidance.

### Change OpenAI Model
In `backend/services/openai_service.py`, change the model:
```python
model="gpt-4o"  # or 'gpt-4o-mini' for cost efficiency
```

### Styling
Vuetify theme is configured in `frontend/src/plugins/vuetify.js`. Modify the theme object to change colors.

## Production Build

1. **Build frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Start production backend server**
   ```bash
   cd backend
   # Activate venv
   uvicorn main:app --host 0.0.0.0 --port 3001
   ```

3. **Serve static files** - The `frontend/dist` folder contains the built files. Serve them through a reverse proxy like Nginx or configure FastAPI to serve static files.

## Environment Variables

### Backend (`backend/.env`)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PORT`: Backend server port (default: 3001)

## Development Scripts

### Frontend (`frontend/`)
- `npm run dev` - Start Vite dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Backend (`backend/`)
- `python main.py` - Start FastAPI server (development mode with auto-reload)
- `uvicorn main:app --reload --port 3001` - Alternative way to start server

## Notes

- The app uses OpenAI's GPT-4o model by default (can be changed to gpt-4o-mini for lower costs)
- RAG system uses TF-IDF + Cosine Similarity for semantic search (can be enhanced with FAISS or embeddings for production)
- All currency references are in Malaysian Ringgit (RM)
- Financial guidance is tailored for Malaysian residents (EPF, ASB, etc.)
- FastAPI provides automatic API documentation at `/docs` endpoint

## License

MIT
