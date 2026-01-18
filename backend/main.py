from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os
from dotenv import load_dotenv
import httpx
from services.gemini_service import generate_financial_plan, refine_financial_plan
from services.rag_service import get_relevant_context
from services.content_extraction import extract_content, summarize_document
from services.retirement_tools import (
    get_investment_options,
    compare_investments,
    calculate_retirement_projection,
    get_product_details,
    create_investment_order,
    INVESTMENT_PRODUCTS
)
from auth import get_current_user, get_supabase_client, security
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

class InvestmentOptionsRequest(BaseModel):
    risk_tolerance: str
    investment_amount: float
    time_horizon: int
    goals: Optional[List[str]] = None

class CompareInvestmentsRequest(BaseModel):
    product_ids: List[str]

class RetirementProjectionRequest(BaseModel):
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    expected_return: float
    inflation_rate: Optional[float] = 3.0

class InvestmentOrderRequest(BaseModel):
    product_id: str
    amount: float
    payment_method: Optional[str] = "online_banking"

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

# Test endpoint to check auth
@app.get("/api/auth/test")
async def test_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Test authentication without full verification."""
    token = credentials.credentials
    print(f"Received token (first 50 chars): {token[:50]}...")
    
    try:
        # Try to decode without verification first
        import jwt as pyjwt
        unverified = pyjwt.decode(token, options={"verify_signature": False})
        print(f"Unverified payload: {unverified}")
        
        # Now try with verification
        settings = get_settings()
        verified = pyjwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return {"status": "success", "payload": verified}
    except Exception as e:
        return {"status": "error", "message": str(e), "type": type(e).__name__}

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

# ============================================================================
# RETIREMENT PLANNING TOOLS ENDPOINTS
# ============================================================================

@app.get("/api/retirement/products")
async def list_investment_products(current_user: dict = Depends(get_current_user)):
    """List all available investment products."""
    return {
        "products": list(INVESTMENT_PRODUCTS.values()),
        "total": len(INVESTMENT_PRODUCTS)
    }

@app.post("/api/retirement/investment-options")
async def get_investment_options_endpoint(
    request: InvestmentOptionsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get personalized investment options based on user criteria."""
    try:
        result = get_investment_options(
            risk_tolerance=request.risk_tolerance,
            investment_amount=request.investment_amount,
            time_horizon=request.time_horizon,
            goals=request.goals
        )
        return result
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get investment options",
                "message": str(error)
            }
        )

@app.post("/api/retirement/compare")
async def compare_investments_endpoint(
    request: CompareInvestmentsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Compare multiple investment products."""
    try:
        result = compare_investments(request.product_ids)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to compare investments",
                "message": str(error)
            }
        )

@app.post("/api/retirement/projection")
async def calculate_projection_endpoint(
    request: RetirementProjectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Calculate retirement savings projection."""
    try:
        result = calculate_retirement_projection(
            current_age=request.current_age,
            retirement_age=request.retirement_age,
            current_savings=request.current_savings,
            monthly_contribution=request.monthly_contribution,
            expected_return=request.expected_return,
            inflation_rate=request.inflation_rate
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to calculate projection",
                "message": str(error)
            }
        )

@app.get("/api/retirement/product/{product_id}")
async def get_product_details_endpoint(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific investment product."""
    try:
        result = get_product_details(product_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get product details",
                "message": str(error)
            }
        )

@app.post("/api/retirement/order")
async def create_order_endpoint(
    request: InvestmentOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create an investment purchase order."""
    try:
        result = create_investment_order(
            product_id=request.product_id,
            amount=request.amount,
            user_id=current_user['id'],
            payment_method=request.payment_method
        )
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result)
        
        # Optionally save order to database
        try:
            supabase = get_supabase_client()
            supabase.table('investment_orders').insert({
                'user_id': current_user['id'],
                'order_id': result['order_id'],
                'product_id': request.product_id,
                'amount': request.amount,
                'status': result['status'],
                'order_data': result
            }).execute()
        except Exception:
            pass  # Continue even if save fails
        
        return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create order",
                "message": str(error)
            }
        )

# ============================================================================
# FILE UPLOAD ENDPOINTS
# ============================================================================

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
        
        print(f"[UPLOAD] Starting upload for {len(files)} files")
        
        # Store file contents for background extraction
        file_data_list = []
        
        # Validate all files first and store content
        print("[UPLOAD] Step 1: Validating files...")
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
        
        print(f"[UPLOAD] Step 2: Uploading {len(files)} files to worker...")
        
        # Upload files concurrently
        async def upload_single_file(file: UploadFile, file_data: dict):
            print(f"[UPLOAD] Uploading {file.filename}...")
            file_content = file_data['content']
            
            # Prepare multipart form data for worker
            files_data = {
                'file': (file.filename, file_content, file.content_type)
            }
            
            print(f"[UPLOAD] Sending {file.filename} to worker...")
            # Forward request to Cloudflare Worker
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{worker_url}/upload",
                    files=files_data
                )
            
            print(f"[UPLOAD] Worker response for {file.filename}: {response.status_code}")
            
            # Check if upload was successful
            if response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                return {
                    "success": False,
                    "fileName": file.filename,
                    "error": error_data.get('error', 'Upload to worker failed')
                }
            
            result = response.json()
            print(f"[UPLOAD] Worker returned: {result}")
            
            # The worker might return different field names
            # Use originalName if available, otherwise fall back to fileName or the original filename
            file_url = result.get('url') or result.get('fileUrl') or result.get('publicUrl') or result.get('link')
            file_name = result.get('originalName') or result.get('fileName') or result.get('filename') or file.filename
            
            if not file_url:
                print(f"[UPLOAD] ERROR: No URL in worker response")
                return {
                    "success": False,
                    "fileName": file.filename,
                    "error": f"Worker did not return file URL"
                }
            
            print(f"[UPLOAD] Saving to database...")
            # Save upload record to database
            document_id = None
            try:
                supabase = get_supabase_client()
                user_id = current_user['id']
                
                db_result = supabase.table('user_uploaded_documents').insert({
                    'userId': str(user_id),
                    'fileName': file_name,
                    'fileUrl': file_url,
                    'extractionStatus': 'pending'
                }).execute()
                
                # Get the inserted document ID
                if db_result.data and len(db_result.data) > 0:
                    document_id = db_result.data[0].get('id')
                    print(f"[UPLOAD] Document saved with ID: {document_id}")
                
            except Exception as db_error:
                print(f"[UPLOAD] Database error: {db_error}")
                return {
                    "success": False,
                    "fileName": file.filename,
                    "error": f"Database error: {str(db_error)}"
                }
            
            # Schedule background extraction if we have document_id
            if document_id:
                try:
                    background_tasks.add_task(
                        extract_and_store_content,
                        file_url,
                        file_name,
                        file_content,
                        file.content_type,
                        current_user['id'],
                        document_id
                    )
                    print(f"[UPLOAD] Background task scheduled for doc {document_id}")
                except Exception as bg_error:
                    print(f"[UPLOAD] Failed to schedule background task: {bg_error}")
            
            print(f"[UPLOAD] Completed {file.filename}")
            return {
                "success": True,
                "fileName": file_name,
                "fileUrl": file_url,
                "documentId": document_id,
                "extractionStatus": "pending"
            }
        
        # Upload all files concurrently using asyncio.gather
        import asyncio
        print("[UPLOAD] Step 3: Processing uploads concurrently...")
        results = await asyncio.gather(
            *[upload_single_file(file, file_data) for file, file_data in zip(files, file_data_list)],
            return_exceptions=True
        )
        
        print("[UPLOAD] Step 4: Processing results...")
        # Process results
        successful_uploads = []
        failed_uploads = []
        
        for result in results:
            if isinstance(result, Exception):
                print(f"[UPLOAD] Exception: {result}")
                failed_uploads.append({
                    "success": False,
                    "error": str(result)
                })
            elif result.get("success"):
                successful_uploads.append(result)
            else:
                failed_uploads.append(result)
        
        print(f"[UPLOAD] Complete! Success: {len(successful_uploads)}, Failed: {len(failed_uploads)}")
        
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
