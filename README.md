# Financial GPS

**Your Personalized Financial Planner in 5 Minutes**

## Team Members

- **Charles**
- **Azfar**

## Problem Statement

Users are experiencing financial paralysis caused by a fragmented landscape of disconnected services. The high cost of professional advisors and the prevalence of generic, 'one-size-fits-all' tools prevent individuals from receiving the personalized guidance necessary to reach their financial goals.

## Solution Overview

Financial GPS is an AI-powered financial planning platform that provides personalized, actionable financial roadmaps tailored to Malaysian residents. By combining an intuitive questionnaire with advanced RAG (Retrieval-Augmented Generation) technology, we deliver comprehensive financial plans in minutes—not weeks.

**Key Features:**
- 📋 Interactive card-based financial assessment
- 📄 Document upload with Docling OCR for automatic data extraction
- 🤖 AI-powered plan generation using Gemini 2.5 Flash
- 📊 Comprehensive financial reports with actionable strategies
- 💬 AI chat refinement for personalized guidance
- 🎯 Malaysian-specific financial advice (EPF, ASB, etc.)

## Tech Stack

- **Frontend**: Vue 3, Vuetify 3, Vite, Vue Router
- **Backend**: FastAPI (Python 3.11), Uvicorn
- **AI**: Google Gemini 2.5 Flash with RAG
- **Document Processing**: Docling for OCR and document extraction
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth

## Environment Variables

### Backend Environment Variables

Create a `backend/.env` file with the following variables:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Server Configuration
PORT=3001
```

### Frontend Environment Variables

Create a `frontend/.env` file with the following variables:

```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API URL
VITE_API_URL=http://localhost:3001
```

## Setup Instructions

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11**
- **Google Gemini API key** ([Get one here](https://aistudio.google.com/app/apikey))
- **Supabase account** ([Sign up here](https://supabase.com))

### Step-by-Step Setup Guide

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd financial-ai
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your API keys
# GEMINI_API_KEY=your_key_here
# SUPABASE_URL=your_url_here
# SUPABASE_KEY=your_key_here
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env and add your configuration
# VITE_SUPABASE_URL=your_url_here
# VITE_SUPABASE_ANON_KEY=your_key_here
# VITE_API_URL=http://localhost:3001
```

#### 4. Start the Application

Open two terminal windows:

**Terminal 1 - Backend Server:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 3001 or python -m uvicorn main:app --reload --port 3001
```
Backend will run on `http://localhost:3001`

**Terminal 2 - Frontend Development Server:**
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:5173`

#### 5. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the Financial GPS landing page. Click "Start My Financial Plan" to begin!

## How It Works

1. **Landing Page**: Users are greeted with a clear value proposition and CTA
2. **Financial Assessment**: Interactive 6-section questionnaire covering income, expenses, debt, savings, and risk tolerance
3. **Document Upload**: Users can upload financial documents (PDFs, images) which are processed using Docling OCR
4. **AI Plan Generation**: RAG system retrieves relevant financial guidance and Gemini 2.5 Flash generates a personalized plan
5. **Comprehensive Report**: Users receive a detailed financial roadmap with immediate actions and long-term strategies
6. **AI Refinement**: Interactive chat allows users to ask questions and refine their plan

## Project Structure

```
financial-gps/
├── frontend/                 # Vue 3 frontend application
│   ├── src/
│   │   ├── components/      # Reusable Vue components
│   │   ├── views/           # Page components
│   │   ├── router/          # Vue Router configuration
│   │   ├── plugins/         # Vuetify configuration
│   │   └── utils/           # Utility functions (auth, etc.)
│   └── package.json
├── backend/                  # FastAPI Python backend
│   ├── services/            # Business logic services
│   │   ├── gemini_service.py         # Gemini AI integration
│   │   ├── rag_service.py            # RAG implementation
│   │   ├── content_extraction.py     # Docling OCR service
│   │   ├── retirement_tools.py       # Financial calculation tools
│   │   └── user_profile_service.py   # User profile management
│   ├── data/                # Financial playbook and documentation
│   ├── main.py              # FastAPI entry point
│   └── requirements.txt
└── README.md
```

## API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:3001/docs`


