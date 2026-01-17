from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from supabase import create_client, Client
from config import get_settings
from typing import Optional

settings = get_settings()
security = HTTPBearer()

# Initialize Supabase client
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token from Supabase."""
    token = credentials.credentials
    
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token_payload: dict = Depends(verify_token)) -> dict:
    """Get current user from token payload."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Optionally fetch user details from Supabase
    try:
        response = supabase.auth.get_user(token_payload.get("access_token", ""))
        return response.user
    except Exception:
        # Return basic user info from token if fetch fails
        return {
            "id": user_id,
            "email": token_payload.get("email"),
        }


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return supabase
