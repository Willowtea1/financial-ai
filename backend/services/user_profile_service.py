"""
User Profile Service
Handles user profile data storage and retrieval for personalized financial advice.
"""

from typing import Dict, Optional
from auth import get_supabase_client


def save_user_profile(user_id: str, profile_data: Dict) -> Dict:
    """
    Save or update user profile from questionnaire responses.
    
    Args:
        user_id: User's unique identifier
        profile_data: Dictionary containing questionnaire responses
            - aboutYou: Occupation
            - income: Annual income range
            - expenses: Monthly expenses range
            - debt: Debt type
            - savings: Savings range
            - riskTolerance: Risk tolerance level
    
    Returns:
        Dictionary with success status and profile data
    """
    try:
        supabase = get_supabase_client()
        
        # Map frontend field names to database column names
        db_data = {
            'user_id': user_id,
            'occupation': profile_data.get('aboutYou'),
            'annual_income': profile_data.get('income'),
            'monthly_expenses': profile_data.get('expenses'),
            'debt_type': profile_data.get('debt'),
            'savings_range': profile_data.get('savings'),
            'risk_tolerance': profile_data.get('riskTolerance')
        }
        
        # Upsert (insert or update if exists)
        result = supabase.table('user_profiles').upsert(
            db_data,
            on_conflict='user_id'
        ).execute()
        
        return {
            "success": True,
            "profile": result.data[0] if result.data else db_data,
            "message": "Profile saved successfully"
        }
    
    except Exception as error:
        print(f"Error saving user profile: {error}")
        return {
            "success": False,
            "error": str(error),
            "message": "Failed to save profile"
        }


def get_user_profile(user_id: str) -> Optional[Dict]:
    """
    Retrieve user profile data.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Dictionary containing user profile data or None if not found
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('user_profiles')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if result.data:
            # Map database columns back to frontend format for consistency
            profile = result.data
            return {
                "aboutYou": profile.get('occupation'),
                "income": profile.get('annual_income'),
                "expenses": profile.get('monthly_expenses'),
                "debt": profile.get('debt_type'),
                "savings": profile.get('savings_range'),
                "riskTolerance": profile.get('risk_tolerance'),
                "created_at": profile.get('created_at'),
                "updated_at": profile.get('updated_at')
            }
        
        return None
    
    except Exception as error:
        print(f"Error retrieving user profile: {error}")
        return None


def get_user_profile_summary(user_id: str) -> str:
    """
    Get a formatted summary of user profile for AI context.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Formatted string summary of user profile
    """
    profile = get_user_profile(user_id)
    
    if not profile:
        return "No user profile found. User has not completed the financial questionnaire yet."
    
    summary = f"""User Financial Profile:
- Occupation: {profile.get('aboutYou', 'Not specified')}
- Annual Income: RM {profile.get('income', 'Not specified')}
- Monthly Expenses: RM {profile.get('expenses', 'Not specified')}
- Debt: {profile.get('debt', 'Not specified')}
- Savings: RM {profile.get('savings', 'Not specified')}
- Risk Tolerance: {profile.get('riskTolerance', 'Not specified')}
- Profile Last Updated: {profile.get('updated_at', 'Unknown')}"""
    
    return summary


def delete_user_profile(user_id: str) -> Dict:
    """
    Delete user profile data.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Dictionary with success status
    """
    try:
        supabase = get_supabase_client()
        
        supabase.table('user_profiles')\
            .delete()\
            .eq('user_id', user_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Profile deleted successfully"
        }
    
    except Exception as error:
        print(f"Error deleting user profile: {error}")
        return {
            "success": False,
            "error": str(error),
            "message": "Failed to delete profile"
        }


# Tool function for AI to query user profile
def get_user_financial_profile(user_id: str) -> Dict:
    """
    Tool function for AI agents to retrieve user financial profile.
    Returns structured data that AI can use for personalized recommendations.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Dictionary with user profile data and metadata
    """
    profile = get_user_profile(user_id)
    
    if not profile:
        return {
            "found": False,
            "message": "User has not completed the financial questionnaire yet.",
            "suggestion": "Ask the user to complete the questionnaire for personalized advice."
        }
    
    # Parse income and expenses ranges for numerical analysis
    income_map = {
        '0–36,000': {'min': 0, 'max': 36000, 'midpoint': 18000},
        '36,001–60,000': {'min': 36001, 'max': 60000, 'midpoint': 48000},
        '60,001–100,000': {'min': 60001, 'max': 100000, 'midpoint': 80000},
        '100,000+': {'min': 100000, 'max': 200000, 'midpoint': 150000}
    }
    
    expenses_map = {
        '0–1,000': {'min': 0, 'max': 1000, 'midpoint': 500},
        '1,001–2,500': {'min': 1001, 'max': 2500, 'midpoint': 1750},
        '2,501–4,000': {'min': 2501, 'max': 4000, 'midpoint': 3250},
        '4,000+': {'min': 4000, 'max': 8000, 'midpoint': 6000}
    }
    
    income_range = income_map.get(profile.get('income', ''), {})
    expenses_range = expenses_map.get(profile.get('expenses', ''), {})
    
    # Calculate estimated monthly savings capacity
    monthly_income = income_range.get('midpoint', 0) / 12 if income_range else 0
    monthly_expenses = expenses_range.get('midpoint', 0)
    monthly_savings_capacity = max(0, monthly_income - monthly_expenses)
    
    return {
        "found": True,
        "profile": {
            "occupation": profile.get('aboutYou'),
            "annual_income_range": profile.get('income'),
            "monthly_expenses_range": profile.get('expenses'),
            "debt_type": profile.get('debt'),
            "savings_range": profile.get('savings'),
            "risk_tolerance": profile.get('riskTolerance')
        },
        "analysis": {
            "estimated_monthly_income": round(monthly_income, 2),
            "estimated_monthly_expenses": monthly_expenses,
            "estimated_monthly_savings_capacity": round(monthly_savings_capacity, 2),
            "has_debt": profile.get('debt') != 'None',
            "debt_type": profile.get('debt')
        },
        "recommendations": {
            "suitable_for_investing": monthly_savings_capacity > 500,
            "emergency_fund_priority": profile.get('savings') in ['0', '1k–10k'],
            "debt_management_priority": profile.get('debt') not in ['None', None]
        },
        "metadata": {
            "last_updated": profile.get('updated_at'),
            "profile_age": "Recent" if profile.get('updated_at') else "Unknown"
        }
    }
