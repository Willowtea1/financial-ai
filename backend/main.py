from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os
from dotenv import load_dotenv
from services.gemini_service import generate_financial_plan, refine_financial_plan
from services.rag_service import get_relevant_context

load_dotenv()

app = FastAPI(title="Financial GPS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL (e.g., ["http://localhost:5173"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class UserAnswers(BaseModel):
    aboutYou: Optional[str] = None
    income: Optional[str] = None
    expenses: Optional[str] = None
    debt: Optional[str] = None
    savings: Optional[str] = None
    riskTolerance: Optional[str] = None

class RefinePlanRequest(BaseModel):
    message: str
    planData: Dict
    chatHistory: List[Dict] = []

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Generate financial plan
@app.post("/api/generate-plan")
async def generate_plan(user_answers: UserAnswers):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== Received generate-plan request ===")
        logger.info(f"User answers: {user_answers.dict()}")
        
        # Get relevant context from financial playbook using RAG
        logger.info("Getting relevant context from RAG...")
        context = await get_relevant_context(user_answers.dict())
        logger.info(f"Context retrieved: {len(context)} characters")
        
        # Generate financial plan using Gemini
        logger.info("Generating financial plan with Gemini...")
        plan = await generate_financial_plan(user_answers.dict(), context)
        logger.info("Plan generated successfully")
        
        return plan
    except Exception as error:
        logger.error(f"Error generating plan: {error}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate financial plan",
                "message": str(error)
            }
        )

# Refine plan with chat
@app.post("/api/refine-plan")
async def refine_plan(request: RefinePlanRequest):
    try:
        # Get relevant context from financial playbook
        context = await get_relevant_context(request.planData or {})
        
        # Refine plan using OpenAI
        result = await refine_financial_plan(
            request.message,
            request.planData,
            request.chatHistory,
            context
        )
        
        return result
    except Exception as error:
        print(f"Error refining plan: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to refine plan",
                "message": str(error)
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
