from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os
from dotenv import load_dotenv
import httpx
import json
import traceback
import google.generativeai as genai
from datetime import datetime
from services.gemini_service import generate_financial_plan, refine_financial_plan
from services.rag_service import get_relevant_context
from services.content_extraction import extract_content, summarize_document
from services.retirement_tools import (
    get_investment_options,
    compare_investments,
    calculate_retirement_projection,
    get_product_details,
    create_investment_order,
    create_epf_topup_action,
    create_insurance_recommendation,
    create_savings_goal_action,
    INVESTMENT_PRODUCTS
)
from services.user_profile_service import (
    save_user_profile,
    get_user_profile,
    get_user_profile_summary,
    get_user_financial_profile,
    delete_user_profile
)
from auth import get_current_user, get_supabase_client, security
from config import get_settings

load_dotenv()

# Configure Gemini for streaming
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

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

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[Dict]] = []
    context: Optional[Dict] = None

class ExecuteActionRequest(BaseModel):
    action_id: str | int  # Accept both string and int
    action_type: str
    data: Dict

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

# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@app.post("/api/profile")
async def save_profile(
    user_answers: UserAnswers,
    current_user: dict = Depends(get_current_user)
):
    """Save or update user profile from questionnaire."""
    try:
        result = save_user_profile(current_user['id'], user_answers.dict())
        return result
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to save profile",
                "message": str(error)
            }
        )

@app.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile."""
    try:
        profile = get_user_profile(current_user['id'])
        if profile:
            return {"success": True, "profile": profile}
        else:
            return {"success": False, "message": "Profile not found"}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve profile",
                "message": str(error)
            }
        )

@app.delete("/api/profile")
async def delete_profile(current_user: dict = Depends(get_current_user)):
    """Delete current user's profile."""
    try:
        result = delete_user_profile(current_user['id'])
        return result
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete profile",
                "message": str(error)
            }
        )

# ============================================================================
# FINANCIAL PLAN GENERATION
# ============================================================================

# Generate financial plan (protected)
@app.post("/api/generate-plan")
async def generate_plan(
    user_answers: UserAnswers,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Save user profile first
        save_user_profile(current_user['id'], user_answers.dict())
        
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
# STREAMING QUERY ENDPOINT
# ============================================================================

@app.post("/api/query")
async def stream_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Stream AI responses to user queries in real-time with function calling support.
    Supports chat history, context, and can use retirement planning tools.
    """
    print("\n" + "="*80)
    print("[STREAM QUERY] New request received")
    print(f"[STREAM QUERY] User ID: {current_user.get('id', 'unknown')}")
    print(f"[STREAM QUERY] Query: {request.query[:100]}...")
    print(f"[STREAM QUERY] Chat history length: {len(request.chat_history) if request.chat_history else 0}")
    print(f"[STREAM QUERY] Context provided: {bool(request.context)}")
    print("="*80 + "\n")
    
    async def generate_stream():
        try:
            print("[STREAM] Starting stream generation with function calling...")
            
            # Get user profile summary for personalization
            user_profile_summary = get_user_profile_summary(current_user.get('id'))
            print(f"[STREAM] User profile: {user_profile_summary[:100]}...")
            
            # Get user's uploaded documents summaries
            document_summaries = ""
            try:
                supabase = get_supabase_client()
                docs_result = supabase.table('user_uploaded_documents')\
                    .select('fileName, summary, extractionStatus')\
                    .eq('userId', str(current_user.get('id')))\
                    .eq('extractionStatus', 'completed')\
                    .execute()
                
                if docs_result.data and len(docs_result.data) > 0:
                    document_summaries = "\n\nUser's Financial Documents:\n"
                    for doc in docs_result.data:
                        if doc.get('summary'):
                            document_summaries += f"\n- {doc['fileName']}:\n{doc['summary']}\n"
                    print(f"[STREAM] Found {len(docs_result.data)} document summaries")
                else:
                    print("[STREAM] No document summaries found")
            except Exception as doc_error:
                print(f"[STREAM] Error fetching documents: {doc_error}")
            
            # Get relevant context from RAG if no specific context provided
            rag_context = ""
            if request.context:
                print(f"[STREAM] Fetching RAG context for: {request.context}")
                rag_context = await get_relevant_context(request.context)
                print(f"[STREAM] RAG context length: {len(rag_context)} chars")
            else:
                print("[STREAM] No context provided, skipping RAG")
            
            # Build the conversation prompt with tool instructions
            system_prompt = f"""You are a knowledgeable financial advisor assistant specializing in Malaysian personal finance.
You provide clear, actionable advice on financial planning, investments, retirement planning, and money management.

{user_profile_summary}

{document_summaries}

IMPORTANT: You have access to powerful retirement planning tools that you SHOULD USE when relevant:

1. **get_user_financial_profile**: Retrieve detailed user financial profile with analysis
   - Use when you need specific details about the user's financial situation
   - Provides income, expenses, savings capacity, debt info, and personalized recommendations
   
2. **get_investment_options**: Find suitable investment products based on risk tolerance, amount, and time horizon
   - Use when users ask about investment options, what to invest in, or need recommendations
   
3. **compare_investments**: Compare multiple investment products side by side
   - Use when users want to compare different investment options
   
4. **calculate_retirement_projection**: Calculate retirement savings projections with future value
   - Use when users ask about retirement planning, how much they'll have, or need projections
   
5. **get_product_details**: Get detailed information about specific investment products
   - Use when users ask about a specific product or want more details
   
6. **create_investment_order**: Help users purchase investments (use carefully, confirm intent first)
   - Use when users explicitly want to invest or purchase a product

WHEN TO USE TOOLS:
- User asks "What should I invest in?" → Use get_investment_options with their profile data
- User asks "How much will I have at retirement?" → Use calculate_retirement_projection
- User mentions age, savings, monthly amount → Proactively use calculate_retirement_projection
- User asks about specific products → Use get_product_details
- User wants to compare options → Use compare_investments
- You need their exact financial details → Use get_user_financial_profile

IMPORTANT: When you use a tool, explain what you're doing and present the results clearly.

Guidelines:
- Use Malaysian Ringgit (RM) currency
- Be conversational and helpful
- Provide specific, actionable advice tailored to the user's profile
- Reference the user's uploaded financial documents when relevant
- Consider both their questionnaire responses AND document data for comprehensive advice
- Reference Malaysian financial context (EPF, KWSP, taxes, etc.) when relevant
- Use the tools proactively to provide data-driven recommendations
- Use markdown formatting for better readability
- When presenting tool results, format them nicely with tables or lists
- If you notice discrepancies between questionnaire data and documents, ask for clarification"""

            if rag_context:
                system_prompt += f"\n\nRelevant Financial Guidance:\n{rag_context}"

            # Build conversation history
            conversation_parts = [system_prompt]
            
            # Add chat history (last 10 messages)
            recent_history = request.chat_history[-10:] if request.chat_history else []
            print(f"[STREAM] Adding {len(recent_history)} messages from history")
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conversation_parts.append(f"{role.upper()}: {content}")
            
            # Add current query
            conversation_parts.append(f"USER: {request.query}")
            conversation_parts.append("ASSISTANT:")
            
            conversation = "\n\n".join(conversation_parts)
            print(f"[STREAM] Total conversation length: {len(conversation)} chars")

            # Import the tool-enabled model from gemini_service
            from services.gemini_service import model as tool_model, execute_tool
            
            print("[STREAM] Starting chat with function calling enabled...")
            chat = tool_model.start_chat(enable_automatic_function_calling=False)
            
            # Send initial message
            response = chat.send_message(
                conversation,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=4000,  # Increased from 2000
                ),
                stream=True
            )
            
            print("[STREAM] Processing response chunks...")
            chunk_count = 0
            total_chars = 0
            
            # Process streaming response
            for chunk in response:
                # Check for function calls
                if chunk.candidates and len(chunk.candidates) > 0:
                    candidate = chunk.candidates[0]
                    
                    # Check finish reason
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                        print(f"[STREAM] Finish reason: {candidate.finish_reason}")
                    
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            # Handle function call
                            if hasattr(part, 'function_call') and part.function_call:
                                function_call = part.function_call
                                tool_name = function_call.name
                                
                                # Extract parameters
                                parameters = {}
                                for key, value in function_call.args.items():
                                    parameters[key] = value
                                
                                # Add user_id if the tool needs it
                                if tool_name in ["create_investment_order", "create_epf_topup_action"]:
                                    parameters["user_id"] = current_user.get('id')
                                
                                print(f"[STREAM TOOL CALL] {tool_name} with params: {parameters}")
                                
                                # Send tool call notification to client with better formatting
                                tool_display_names = {
                                    "get_user_financial_profile": "📊 Analyzing your financial profile",
                                    "get_investment_options": "🔍 Finding suitable investment options",
                                    "compare_investments": "⚖️ Comparing investment products",
                                    "calculate_retirement_projection": "📈 Calculating retirement projection",
                                    "get_product_details": "📋 Getting product details",
                                    "create_investment_order": "💰 Creating investment order",
                                    "create_epf_topup_action": "🏦 Preparing EPF top-up",
                                    "create_insurance_recommendation": "🛡️ Finding insurance options",
                                    "create_savings_goal_action": "🎯 Setting up savings goal"
                                }
                                
                                tool_display = tool_display_names.get(tool_name, f"🔧 Using tool: {tool_name}")
                                tool_msg = f"\n\n*{tool_display}...*\n\n"
                                data = json.dumps({"content": tool_msg, "toolCall": tool_name})
                                yield f"data: {data}\n\n"
                                
                                # Execute the tool
                                tool_result = execute_tool(tool_name, parameters)
                                print(f"[STREAM TOOL RESULT] {str(tool_result)[:200]}...")
                                
                                # Check if tool result contains action_card
                                if isinstance(tool_result, dict) and 'action_card' in tool_result:
                                    print(f"[STREAM] Action card detected: {tool_result['action_card']['type']}")
                                    # Send action card to frontend
                                    action_card_data = json.dumps({
                                        "action_card": tool_result['action_card'],
                                        "content": ""  # Empty content, action card will be displayed separately
                                    })
                                    yield f"data: {action_card_data}\n\n"
                                
                                # Send tool result back to model and continue streaming
                                follow_up = chat.send_message(
                                    genai.protos.Content(
                                        parts=[genai.protos.Part(
                                            function_response=genai.protos.FunctionResponse(
                                                name=tool_name,
                                                response={"result": tool_result}
                                            )
                                        )]
                                    ),
                                    generation_config=genai.GenerationConfig(
                                        temperature=0.7,
                                        max_output_tokens=4000,
                                    ),
                                    stream=True
                                )
                                
                                # Stream the follow-up response
                                for follow_chunk in follow_up:
                                    # Check if chunk has candidates and parts
                                    if follow_chunk.candidates and len(follow_chunk.candidates) > 0:
                                        follow_candidate = follow_chunk.candidates[0]
                                        
                                        # Check finish reason
                                        if hasattr(follow_candidate, 'finish_reason') and follow_candidate.finish_reason:
                                            print(f"[STREAM] Follow-up finish reason: {follow_candidate.finish_reason}")
                                        
                                        if follow_candidate.content and follow_candidate.content.parts:
                                            for follow_part in follow_candidate.content.parts:
                                                # Only process text parts
                                                if hasattr(follow_part, 'text') and follow_part.text:
                                                    chunk_count += 1
                                                    total_chars += len(follow_part.text)
                                                    if chunk_count <= 3:
                                                        print(f"[STREAM] Chunk {chunk_count}: {follow_part.text[:50]}...")
                                                    elif chunk_count % 10 == 0:
                                                        print(f"[STREAM] Chunk {chunk_count} (total chars: {total_chars})")
                                                    
                                                    data = json.dumps({"content": follow_part.text})
                                                    yield f"data: {data}\n\n"
                            
                            # Handle regular text
                            elif hasattr(part, 'text') and part.text:
                                chunk_count += 1
                                total_chars += len(part.text)
                                if chunk_count <= 3:
                                    print(f"[STREAM] Chunk {chunk_count}: {part.text[:50]}...")
                                elif chunk_count % 10 == 0:
                                    print(f"[STREAM] Chunk {chunk_count} (total chars: {total_chars})")
                                
                                data = json.dumps({"content": part.text})
                                yield f"data: {data}\n\n"
            
            print(f"[STREAM] Streaming complete! Total chunks: {chunk_count}, Total chars: {total_chars}")
            
            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            print("[STREAM] Sent completion signal")

        except Exception as error:
            print(f"[STREAM ERROR] Exception occurred: {error}")
            print(f"[STREAM ERROR] Error type: {type(error).__name__}")
            print(f"[STREAM ERROR] Traceback:\n{traceback.format_exc()}")
            
            error_data = json.dumps({
                "error": str(error),
                "done": True
            })
            yield f"data: {error_data}\n\n"
            print("[STREAM ERROR] Sent error to client")

    print("[STREAM] Returning StreamingResponse...")
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
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

# ============================================================================
# ACTION EXECUTION ENDPOINT
# ============================================================================

@app.post("/api/execute-action")
async def execute_action(
    request: ExecuteActionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a financial action approved by user.
    Handles investment purchases, EPF top-ups, insurance purchases, and savings goals.
    """
    try:
        action_type = request.action_type
        data = request.data
        user_id = current_user['id']
        
        print(f"[EXECUTE ACTION] Type: {action_type}, User: {user_id}")
        print(f"[EXECUTE ACTION] Data: {data}")
        
        result = {}
        
        if action_type == 'investment':
            # Process investment purchase
            result = create_investment_order(
                product_id=data.get('productId'),
                amount=data.get('amount'),
                user_id=user_id,
                payment_method=data.get('paymentMethod', 'online_banking')
            )
            
            # Save to database
            try:
                supabase = get_supabase_client()
                supabase.table('investment_orders').insert({
                    'user_id': user_id,
                    'order_id': result.get('order_id'),
                    'product_id': data.get('productId'),
                    'amount': data.get('amount'),
                    'status': result.get('status'),
                    'order_data': result
                }).execute()
            except Exception as db_error:
                print(f"[EXECUTE ACTION] DB save failed: {db_error}")
            
        elif action_type == 'epf_topup':
            # Process EPF top-up
            result = create_epf_topup_action(
                amount=data.get('amount'),
                user_id=user_id
            )
            
            # In production, this would integrate with EPF's API
            # For now, return the payment URL
            result['message'] = 'EPF top-up initiated. Redirecting to payment portal...'
            
        elif action_type == 'insurance':
            # Process insurance purchase
            # In production, this would integrate with insurance provider's API
            result = {
                'success': True,
                'policy_number': f"POL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'product_id': data.get('productId'),
                'coverage': data.get('coverage'),
                'premium': data.get('premium'),
                'status': 'active',
                'message': 'Insurance policy activated successfully!'
            }
            
            # Save to database
            try:
                supabase = get_supabase_client()
                supabase.table('insurance_policies').insert({
                    'user_id': user_id,
                    'policy_number': result['policy_number'],
                    'product_id': data.get('productId'),
                    'coverage': data.get('coverage'),
                    'premium': data.get('premium'),
                    'status': 'active',
                    'policy_data': result
                }).execute()
            except Exception as db_error:
                print(f"[EXECUTE ACTION] DB save failed: {db_error}")
            
        elif action_type == 'savings_goal':
            # Set up savings goal
            result = create_savings_goal_action(
                goal_name=data.get('goalName'),
                target_amount=data.get('targetAmount'),
                months=data.get('months')
            )
            
            # Save to database
            try:
                supabase = get_supabase_client()
                supabase.table('savings_goals').insert({
                    'user_id': user_id,
                    'goal_id': result.get('action_id'),
                    'goal_name': data.get('goalName'),
                    'target_amount': data.get('targetAmount'),
                    'monthly_amount': data.get('monthlyAmount'),
                    'months': data.get('months'),
                    'status': 'active',
                    'goal_data': result
                }).execute()
            except Exception as db_error:
                print(f"[EXECUTE ACTION] DB save failed: {db_error}")
            
            result['message'] = 'Savings goal created successfully!'
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action type: {action_type}"
            )
        
        print(f"[EXECUTE ACTION] Success: {result.get('success', False)}")
        return {
            "success": True,
            "result": result,
            "action_id": request.action_id,
            "action_type": action_type
        }
        
    except HTTPException:
        raise
    except Exception as error:
        print(f"[EXECUTE ACTION] Error: {error}")
        print(f"[EXECUTE ACTION] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to execute action",
                "message": str(error)
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
