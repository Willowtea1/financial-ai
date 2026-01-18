# Quick Setup Guide - Financial AI

## Prerequisites

- **Node.js 18+** and npm
- **Python 3.9+**
- **OpenAI API key** (get from https://platform.openai.com/api-keys)

## Step-by-Step Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 2. Set Up Python Backend

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

### 3. Configure Environment Variables

Create `backend/.env` file:

```bash
cd backend
# Copy example file
cp .env.example .env
```

Edit `backend/.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
PORT=3001
```

### 4. Start Development Servers

**Terminal 1 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:5173`

**Terminal 2 - Backend:**
```bash
cd backend
# Make sure venv is activated
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Start FastAPI server
python main.py
```
Backend will run on `http://localhost:3001`

### 5. Access the Application

Open your browser and navigate to: `http://localhost:5173`

## API Documentation

Once the backend is running, you can access:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## Troubleshooting

### Python/venv Issues

**If `python` command not found:**
- Try `python3` instead
- Make sure Python 3.9+ is installed

**If virtual environment activation fails:**
- Windows: Make sure you're using PowerShell or Command Prompt (not Git Bash)
- Try: `python -m venv venv --clear` to recreate

### Port Already in Use

If port 3001 is already in use:
1. Change `PORT` in `backend/.env` to a different port (e.g., 3002)
2. Update `frontend/vite.config.js` proxy target to match

### OpenAI API Errors

- Verify your API key is correct in `backend/.env`
- Check your OpenAI account has credits
- Ensure the API key has proper permissions

### Module Not Found Errors

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Backend:**
```bash
cd backend
# Activate venv first
pip install -r requirements.txt
```

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

### Run Backend in Production
```bash
cd backend
# Activate venv
uvicorn main:app --host 0.0.0.0 --port 3001
```

## Project Structure

```
financial-gps/
├── frontend/          # Vue 3 + Vite
│   └── src/          # Vue components and views
├── backend/          # FastAPI Python backend
│   ├── main.py       # FastAPI app
│   ├── services/     # Business logic
│   └── data/         # Financial playbook
└── README.md         # Full documentation
```
