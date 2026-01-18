from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os
from dotenv import load_dotenv
import httpx
from services.gemini_service import generate_financial_plan, refine_financial_plan
from services.rag_service import get_relevant_context
from services.content_extraction import extract_content, summarize_document
from auth import get_current_user, get_supabase_client
from config import get_settings

load_dotenv()

app = FastAPI(title="Financial GPS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # specify frontend URL in production
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

class GoogleAuthRequest(BaseModel):
    id_token: str

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Auth endpoints
@app.post("/api/auth/google")
async def google_auth(auth_request: GoogleAuthRequest):
    """Authenticate with Google OAuth token."""
    try:
        supabase = get_supabase_client()
        
        # Sign in with Google ID token
        response = supabase.auth.sign_in_with_id_token({
            "provider": "google",
            "token": auth_request.id_token
        })
        
        return {
            "user": response.user,
            "session": response.session,
            "access_token": response.session.access_token
        }
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Authentication failed: {str(error)}"
        )

@app.post("/api/auth/signout")
async def signout(current_user: dict = Depends(get_current_user)):
    """Sign out current user."""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Sign out failed: {str(error)}"
        )

@app.get("/api/auth/user")
async def get_user(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user

# Generate financial plan (protected)
@app.post("/api/generate-plan")
async def generate_plan(
    user_answers: UserAnswers,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get relevant context from financial playbook using RAG
        context = await get_relevant_context(user_answers.dict())
        
        # Generate financial plan using Gemini
        plan = await generate_financial_plan(user_answers.dict(), context)
        
        # Optionally save plan to Supabase for the user
        try:
            supabase = get_supabase_client()
            supabase.table('financial_plans').insert({
                'user_id': current_user['id'],
                'plan_data': plan,
                'user_answers': user_answers.dict()
            }).execute()
        except Exception:
            pass  # Continue even if save fails
        
        return plan
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate financial plan",
                "message": str(error)
            }
        )

# Refine plan with chat (protected)
@app.post("/api/refine-plan")
async def refine_plan(
    request: RefinePlanRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get relevant context from financial playbook
        context = await get_relevant_context(request.planData or {})
        
        # Refine plan using Gemini
        result = await refine_financial_plan(
            request.message,
            request.planData,
            request.chatHistory,
            context
        )
        
        return result
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to refine plan",
                "message": str(error)
            }
        )

# Background task to extract content from uploaded file
async def extract_and_store_content(
    file_url: str,
    file_name: str,
    file_content: bytes,
    content_type: str,
    user_id: str,
    document_id: int
):
    """
    Background task to extract content from uploaded file, summarize it, and update database.
    """
    try:
        # Extract content
        extracted_text = await extract_content(file_content, content_type, file_name)
        
        # Generate summary
        summary = await summarize_document(extracted_text, file_name)
        
        # Update database with extracted content and summary
        supabase = get_supabase_client()
        supabase.table('user_uploaded_documents').update({
            'extractedContent': extracted_text,
            'summary': summary,
            'extractionStatus': 'completed'
        }).eq('id', document_id).execute()
        
        print(f"Successfully extracted and summarized content from {file_name}")
    except Exception as e:
        print(f"Failed to extract content from {file_name}: {str(e)}")
        # Update status to failed
        try:
            supabase = get_supabase_client()
            supabase.table('user_uploaded_documents').update({
                'extractionStatus': 'failed',
                'extractionError': str(e)
            }).eq('id', document_id).execute()
        except:
            pass


# Upload files to Cloudflare Worker (protected)
@app.post("/api/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload user documents to R2 storage via Cloudflare Worker.
    Supports multiple files (max 10MB each) uploaded concurrently.
    Content extraction runs in background after upload.
    """
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    try:
        settings = get_settings()
        worker_url = settings.worker_url
        
        # Store file contents for background extraction
        file_data_list = []
        
        # Validate all files first and store content
        for file in files:
            if not file.content_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type could not be determined for {file.filename}"
                )
            
            # Read file to check size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds 10MB limit"
                )
            
            # Store file data for later use
            file_data_list.append({
                'filename': file.filename,
                'content': file_content,
                'content_type': file.content_type
            })
            
            # Reset file pointer for upload
            await file.seek(0)
        
        # Upload files concurrently
        async def upload_single_file(file: UploadFile, file_data: dict):
            file_content = file_data['content']
            
            # Prepare multipart form data for worker
            files_data = {
                'file': (file.filename, file_content, file.content_type)
            }
            
            # Forward request to Cloudflare Worker
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{worker_url}/upload",
                    files=files_data
                )
            
            # Check if upload was successful
            if response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                return {
                    "success": False,
                    "fileName": file.filename,
                    "error": error_data.get('error', 'Upload to worker failed')
                }
            
            result = response.json()
            
            # Save upload record to database
            document_id = None
            try:
                supabase = get_supabase_client()
                db_result = supabase.table('user_uploaded_documents').insert({
                    'userId': current_user['id'],
                    'fileName': result.get('fileName'),
                    'fileUrl': result.get('url'),
                    'extractionStatus': 'pending'
                }).execute()
                
                # Get the inserted document ID
                if db_result.data and len(db_result.data) > 0:
                    document_id = db_result.data[0].get('id')
                
            except Exception as db_error:
                print(f"Failed to save to database: {str(db_error)}")
            
            # Schedule background extraction if we have document_id
            if document_id:
                background_tasks.add_task(
                    extract_and_store_content,
                    result.get('url'),
                    result.get('fileName'),
                    file_content,
                    file.content_type,
                    current_user['id'],
                    document_id
                )
            
            return {
                "success": True,
                "fileName": result.get('fileName'),
                "fileUrl": result.get('url'),
                "documentId": document_id,
                "extractionStatus": "pending"
            }
        
        # Upload all files concurrently using asyncio.gather
        import asyncio
        results = await asyncio.gather(
            *[upload_single_file(file, file_data) for file, file_data in zip(files, file_data_list)],
            return_exceptions=True
        )
        
        # Process results
        successful_uploads = []
        failed_uploads = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_uploads.append({
                    "success": False,
                    "error": str(result)
                })
            elif result.get("success"):
                successful_uploads.append(result)
            else:
                failed_uploads.append(result)
        
        return {
            "successful": successful_uploads,
            "failed": failed_uploads,
            "total": len(files),
            "successCount": len(successful_uploads),
            "failedCount": len(failed_uploads),
            "message": "Files uploaded successfully. Content extraction is processing in the background."
        }
        
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to upload files",
                "message": str(error)
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
