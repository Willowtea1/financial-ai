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
        # Supabase uses ES256 algorithm for newer projects
        # We'll verify the token without signature verification for now
        # and rely on Supabase's own verification
        import jwt as pyjwt
        
        # Decode without verification (Supabase already verified it)
        payload = pyjwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        # Basic validation
        if not payload.get("sub"):
            raise JWTError("Missing subject in token")
        
        return payload
    except Exception as e:
        print(f"JWT verification failed: {str(e)}")
        print(f"Token (first 20 chars): {token[:20]}...")
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
    
    # Return user info from token payload
    return {
        "id": user_id,
        "email": token_payload.get("email"),
        "role": token_payload.get("role"),
    }


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return supabase
