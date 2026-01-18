"""
Retirement Planning Tools for AI Agent Function Calling
Provides investment options, comparisons, and purchase capabilities for retirement planning.
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from services.user_profile_service import get_user_financial_profile

# Mock data for investment products (in production, this would come from a real API)
INVESTMENT_PRODUCTS = {
    "epf": {
        "id": "epf_account_1",
        "name": "EPF Account 1 (Conventional)",
        "type": "retirement_fund",
        "provider": "Employees Provident Fund",
        "returns": {
            "2023": 5.50,
            "2022": 5.35,
            "2021": 6.10,
            "average_5yr": 5.65
        },
        "risk_level": "low",
        "minimum_investment": 0,
        "fees": {
            "management_fee": 0,
            "transaction_fee": 0
        },
        "liquidity": "low",
        "description": "Government-mandated retirement savings with guaranteed returns",
        "features": ["Tax deductible", "Government guaranteed", "Employer contribution"],
        "suitable_for": ["Conservative investors", "Long-term retirement planning"]
    },
    "prs_conservative": {
        "id": "prs_cons_1",
        "name": "PRS Conservative Fund",
        "type": "private_retirement_scheme",
        "provider": "Public Mutual",
        "returns": {
            "2023": 4.20,
            "2022": 3.80,
            "2021": 4.50,
            "average_5yr": 4.10
        },
        "risk_level": "low",
        "minimum_investment": 100,
        "fees": {
            "management_fee": 0.50,
            "transaction_fee": 0
        },
        "liquidity": "medium",
        "description": "Low-risk retirement fund with stable returns",
        "features": ["Tax relief up to RM3,000", "Flexible contributions", "Professional management"],
        "suitable_for": ["Risk-averse investors", "Near retirement age"]
    },
    "prs_moderate": {
        "id": "prs_mod_1",
        "name": "PRS Moderate Fund",
        "type": "private_retirement_scheme",
        "provider": "Manulife",
        "returns": {
            "2023": 6.80,
            "2022": 5.20,
            "2021": 8.30,
            "average_5yr": 6.50
        },
        "risk_level": "medium",
        "minimum_investment": 100,
        "fees": {
            "management_fee": 0.75,
            "transaction_fee": 0
        },
        "liquidity": "medium",
        "description": "Balanced fund with mix of equity and fixed income",
        "features": ["Tax relief up to RM3,000", "Diversified portfolio", "Professional management"],
        "suitable_for": ["Moderate risk tolerance", "10-20 years to retirement"]
    },
    "prs_growth": {
        "id": "prs_growth_1",
        "name": "PRS Growth Fund",
        "type": "private_retirement_scheme",
        "provider": "Principal",
        "returns": {
            "2023": 9.50,
            "2022": -2.30,
            "2021": 15.20,
            "average_5yr": 8.80
        },
        "risk_level": "high",
        "minimum_investment": 100,
        "fees": {
            "management_fee": 1.00,
            "transaction_fee": 0
        },
        "liquidity": "medium",
        "description": "Equity-focused fund for long-term capital growth",
        "features": ["Tax relief up to RM3,000", "High growth potential", "Professional management"],
        "suitable_for": ["Aggressive investors", "20+ years to retirement"]
    },
    "unit_trust_equity": {
        "id": "ut_equity_1",
        "name": "Malaysian Equity Fund",
        "type": "unit_trust",
        "provider": "Kenanga",
        "returns": {
            "2023": 12.30,
            "2022": -5.20,
            "2021": 18.50,
            "average_5yr": 10.20
        },
        "risk_level": "high",
        "minimum_investment": 1000,
        "fees": {
            "management_fee": 1.50,
            "sales_charge": 5.00,
            "transaction_fee": 0
        },
        "liquidity": "high",
        "description": "Invests primarily in Malaysian equities for capital appreciation",
        "features": ["High liquidity", "Professional fund management", "Diversified portfolio"],
        "suitable_for": ["Long-term investors", "High risk tolerance"]
    },
    "unit_trust_balanced": {
        "id": "ut_balanced_1",
        "name": "Balanced Growth Fund",
        "type": "unit_trust",
        "provider": "CIMB-Principal",
        "returns": {
            "2023": 7.80,
            "2022": 2.10,
            "2021": 10.50,
            "average_5yr": 7.20
        },
        "risk_level": "medium",
        "minimum_investment": 1000,
        "fees": {
            "management_fee": 1.25,
            "sales_charge": 3.00,
            "transaction_fee": 0
        },
        "liquidity": "high",
        "description": "Balanced allocation between equities and fixed income",
        "features": ["Moderate risk", "Regular income potential", "Capital growth"],
        "suitable_for": ["Balanced investors", "Medium-term goals"]
    },
    "robo_advisor": {
        "id": "robo_1",
        "name": "StashAway Risk Index 22%",
        "type": "robo_advisor",
        "provider": "StashAway",
        "returns": {
            "2023": 8.90,
            "2022": -8.50,
            "2021": 14.20,
            "average_5yr": 7.80
        },
        "risk_level": "medium",
        "minimum_investment": 1,
        "fees": {
            "management_fee": 0.80,
            "transaction_fee": 0
        },
        "liquidity": "high",
        "description": "Automated portfolio management with global diversification",
        "features": ["Low minimum", "Auto-rebalancing", "Global diversification", "Tax optimization"],
        "suitable_for": ["Tech-savvy investors", "Hands-off approach", "Global exposure"]
    }
}


def get_investment_options(
    risk_tolerance: str,
    investment_amount: float,
    time_horizon: int,
    goals: Optional[List[str]] = None
) -> Dict:
    """
    Get suitable investment options based on user criteria.
    
    Args:
        risk_tolerance: User's risk tolerance (low, medium, high)
        investment_amount: Amount available to invest in RM
        time_horizon: Years until retirement
        goals: Optional list of investment goals
    
    Returns:
        Dictionary with recommended investment options
    """
    risk_map = {
        "low": ["low"],
        "medium": ["low", "medium"],
        "high": ["low", "medium", "high"]
    }
    
    acceptable_risks = risk_map.get(risk_tolerance.lower(), ["low", "medium"])
    
    # Filter products based on criteria
    suitable_products = []
    for product_id, product in INVESTMENT_PRODUCTS.items():
        # Check risk level
        if product["risk_level"] not in acceptable_risks:
            continue
        
        # Check minimum investment
        if investment_amount < product["minimum_investment"]:
            continue
        
        # Add suitability score based on time horizon
        score = 0
        if time_horizon >= 20 and product["risk_level"] == "high":
            score = 95
        elif time_horizon >= 10 and product["risk_level"] == "medium":
            score = 90
        elif time_horizon < 10 and product["risk_level"] == "low":
            score = 95
        else:
            score = 70
        
        product_copy = product.copy()
        product_copy["suitability_score"] = score
        suitable_products.append(product_copy)
    
    # Sort by suitability score
    suitable_products.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    return {
        "total_options": len(suitable_products),
        "investment_amount": investment_amount,
        "risk_tolerance": risk_tolerance,
        "time_horizon": time_horizon,
        "recommendations": suitable_products[:5],  # Top 5 recommendations
        "timestamp": datetime.now().isoformat()
    }


def compare_investments(product_ids: List[str]) -> Dict:
    """
    Compare multiple investment products side by side.
    
    Args:
        product_ids: List of product IDs to compare
    
    Returns:
        Comparison data for the selected products
    """
    if not product_ids or len(product_ids) < 2:
        return {
            "error": "Please provide at least 2 product IDs to compare",
            "available_products": list(INVESTMENT_PRODUCTS.keys())
        }
    
    comparison = {
        "products": [],
        "comparison_date": datetime.now().isoformat()
    }
    
    for product_id in product_ids:
        if product_id in INVESTMENT_PRODUCTS:
            comparison["products"].append(INVESTMENT_PRODUCTS[product_id])
        else:
            comparison.setdefault("warnings", []).append(
                f"Product '{product_id}' not found"
            )
    
    if len(comparison["products"]) < 2:
        return {
            "error": "Not enough valid products found for comparison",
            "available_products": list(INVESTMENT_PRODUCTS.keys())
        }
    
    # Add comparison insights
    returns = [p["returns"]["average_5yr"] for p in comparison["products"]]
    fees = [p["fees"]["management_fee"] for p in comparison["products"]]
    
    comparison["insights"] = {
        "highest_return": {
            "product": max(comparison["products"], key=lambda x: x["returns"]["average_5yr"])["name"],
            "return": max(returns)
        },
        "lowest_fees": {
            "product": min(comparison["products"], key=lambda x: x["fees"]["management_fee"])["name"],
            "fee": min(fees)
        },
        "average_return": sum(returns) / len(returns),
        "average_fee": sum(fees) / len(fees)
    }
    
    return comparison


def calculate_retirement_projection(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    monthly_contribution: float,
    expected_return: float,
    inflation_rate: float = 3.0
) -> Dict:
    """
    Calculate retirement savings projection.
    
    Args:
        current_age: Current age
        retirement_age: Target retirement age
        current_savings: Current retirement savings in RM
        monthly_contribution: Monthly contribution amount in RM
        expected_return: Expected annual return percentage
        inflation_rate: Expected inflation rate percentage (default 3%)
    
    Returns:
        Projection of retirement savings
    """
    years_to_retirement = retirement_age - current_age
    
    if years_to_retirement <= 0:
        return {
            "error": "Retirement age must be greater than current age"
        }
    
    # Calculate future value with monthly contributions
    monthly_rate = expected_return / 100 / 12
    months = years_to_retirement * 12
    
    # Future value of current savings
    fv_current = current_savings * ((1 + expected_return/100) ** years_to_retirement)
    
    # Future value of monthly contributions (annuity)
    if monthly_rate > 0:
        fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        fv_contributions = monthly_contribution * months
    
    total_future_value = fv_current + fv_contributions
    
    # Adjust for inflation
    real_value = total_future_value / ((1 + inflation_rate/100) ** years_to_retirement)
    
    # Calculate total contributions
    total_contributed = current_savings + (monthly_contribution * months)
    investment_gains = total_future_value - total_contributed
    
    return {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "years_to_retirement": years_to_retirement,
        "current_savings": current_savings,
        "monthly_contribution": monthly_contribution,
        "expected_annual_return": expected_return,
        "inflation_rate": inflation_rate,
        "projection": {
            "total_future_value": round(total_future_value, 2),
            "real_value_today": round(real_value, 2),
            "total_contributed": round(total_contributed, 2),
            "investment_gains": round(investment_gains, 2),
            "return_on_investment": round((investment_gains / total_contributed * 100), 2) if total_contributed > 0 else 0
        },
        "monthly_income_at_retirement": {
            "4_percent_rule": round(total_future_value * 0.04 / 12, 2),
            "3_percent_rule": round(total_future_value * 0.03 / 12, 2)
        },
        "recommendation": "Consider increasing contributions" if total_future_value < 1000000 else "On track for comfortable retirement"
    }


def create_investment_order(
    product_id: str,
    amount: float,
    user_id: str,
    payment_method: str = "online_banking"
) -> Dict:
    """
    Create an investment purchase order.
    
    Args:
        product_id: ID of the investment product
        amount: Investment amount in RM
        user_id: User identifier
        payment_method: Payment method (online_banking, fpx, credit_card)
    
    Returns:
        Order details and payment information
    """
    if product_id not in INVESTMENT_PRODUCTS:
        return {
            "success": False,
            "error": f"Product '{product_id}' not found",
            "available_products": list(INVESTMENT_PRODUCTS.keys())
        }
    
    product = INVESTMENT_PRODUCTS[product_id]
    
    # Validate minimum investment
    if amount < product["minimum_investment"]:
        return {
            "success": False,
            "error": f"Minimum investment for {product['name']} is RM{product['minimum_investment']}"
        }
    
    # Calculate fees
    sales_charge = product["fees"].get("sales_charge", 0)
    sales_charge_amount = amount * (sales_charge / 100)
    net_investment = amount - sales_charge_amount
    
    # Generate order
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{product_id[:4].upper()}"
    
    order = {
        "success": True,
        "order_id": order_id,
        "status": "pending_payment",
        "product": {
            "id": product_id,
            "name": product["name"],
            "provider": product["provider"],
            "type": product["type"]
        },
        "investment_details": {
            "gross_amount": amount,
            "sales_charge": sales_charge_amount,
            "net_investment": net_investment,
            "currency": "MYR"
        },
        "user_id": user_id,
        "payment_method": payment_method,
        "payment_url": f"https://payment.financialgps.com/checkout/{order_id}",
        "created_at": datetime.now().isoformat(),
        "expires_at": datetime.now().isoformat(),  # In production, add 30 minutes
        "next_steps": [
            "Complete payment via the payment URL",
            "Receive confirmation email",
            "Investment will be processed within 2-3 business days",
            "View investment in your portfolio dashboard"
        ],
        # Add action card data for frontend
        "action_card": {
            "type": "investment",
            "title": f"Invest in {product['name']}",
            "description": f"Ready to invest RM {amount:,.2f} in {product['name']}?",
            "data": {
                "productName": product['name'],
                "productId": product_id,
                "amount": amount,
                "expectedReturn": product['returns']['average_5yr'],
                "riskLevel": product['risk_level'].capitalize(),
                "provider": product['provider']
            }
        }
    }
    
    return order


def create_epf_topup_action(amount: float, user_id: str) -> Dict:
    """
    Create an EPF top-up action card.
    
    Args:
        amount: Top-up amount in RM
        user_id: User identifier
    
    Returns:
        EPF top-up action details
    """
    # Calculate tax relief (max RM 4,000 for EPF top-up)
    max_tax_relief = 4000
    tax_relief = min(amount, max_tax_relief)
    
    action_id = f"EPF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "success": True,
        "action_id": action_id,
        "action_card": {
            "type": "epf_topup",
            "title": "EPF Voluntary Contribution",
            "description": f"Top up your EPF Account 1 with RM {amount:,.2f} and enjoy tax relief!",
            "data": {
                "amount": amount,
                "taxRelief": tax_relief,
                "maxTaxRelief": max_tax_relief,
                "account": "Account 1",
                "method": "Online Banking"
            }
        },
        "payment_url": f"https://secure.kwsp.gov.my/topup/{action_id}",
        "benefits": [
            f"Tax relief up to RM {tax_relief:,.2f}",
            "Guaranteed returns (5.5% dividend in 2023)",
            "Retirement savings boost",
            "Compound interest growth"
        ]
    }


def create_insurance_recommendation(coverage_amount: float, user_profile: Dict) -> Dict:
    """
    Create insurance recommendation action cards.
    
    Args:
        coverage_amount: Desired coverage amount in RM
        user_profile: User's financial profile
    
    Returns:
        Insurance recommendations with action cards
    """
    # Mock insurance products (in production, integrate with real insurance APIs)
    insurance_products = [
        {
            "id": "life_basic",
            "name": "Life Protection Plus",
            "provider": "Great Eastern",
            "coverage": coverage_amount,
            "premium": coverage_amount * 0.002,  # 0.2% of coverage
            "benefits": ["Death benefit", "TPD coverage", "Critical illness rider"],
            "term": "20 years"
        },
        {
            "id": "life_premium",
            "name": "Comprehensive Life Shield",
            "provider": "Prudential",
            "coverage": coverage_amount,
            "premium": coverage_amount * 0.0035,  # 0.35% of coverage
            "benefits": ["Death benefit", "TPD coverage", "Critical illness", "Medical card", "Investment component"],
            "term": "25 years"
        }
    ]
    
    action_cards = []
    for product in insurance_products:
        action_cards.append({
            "type": "insurance",
            "title": product["name"],
            "description": f"Get RM {coverage_amount:,.0f} coverage for just RM {product['premium']:,.2f}/month",
            "data": {
                "productId": product["id"],
                "productName": product["name"],
                "provider": product["provider"],
                "coverage": coverage_amount,
                "premium": product["premium"],
                "benefits": product["benefits"],
                "term": product["term"]
            }
        })
    
    return {
        "success": True,
        "recommendations": action_cards,
        "message": f"Found {len(action_cards)} insurance options matching your needs"
    }


def create_savings_goal_action(goal_name: str, target_amount: float, months: int) -> Dict:
    """
    Create a savings goal action card.
    
    Args:
        goal_name: Name of the savings goal
        target_amount: Target amount in RM
        months: Number of months to reach goal
    
    Returns:
        Savings goal action details
    """
    monthly_amount = target_amount / months
    
    action_id = f"GOAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "success": True,
        "action_id": action_id,
        "action_card": {
            "type": "savings_goal",
            "title": f"Savings Goal: {goal_name}",
            "description": f"Save RM {monthly_amount:,.2f} monthly to reach your goal of RM {target_amount:,.2f}",
            "data": {
                "goalName": goal_name,
                "targetAmount": target_amount,
                "monthlyAmount": monthly_amount,
                "months": months,
                "startDate": datetime.now().isoformat(),
                "endDate": (datetime.now().replace(month=datetime.now().month + months)).isoformat()
            }
        },
        "auto_debit": {
            "enabled": True,
            "amount": monthly_amount,
            "frequency": "monthly",
            "day_of_month": 1
        }
    }


def get_product_details(product_id: str) -> Dict:
    """
    Get detailed information about a specific investment product.
    
    Args:
        product_id: ID of the investment product
    
    Returns:
        Detailed product information
    """
    if product_id not in INVESTMENT_PRODUCTS:
        return {
            "error": f"Product '{product_id}' not found",
            "available_products": list(INVESTMENT_PRODUCTS.keys())
        }
    
    product = INVESTMENT_PRODUCTS[product_id].copy()
    
    # Add additional details
    product["last_updated"] = datetime.now().isoformat()
    product["regulatory_info"] = {
        "regulated_by": "Securities Commission Malaysia" if product["type"] in ["unit_trust", "private_retirement_scheme"] else "Bank Negara Malaysia",
        "investor_protection": "Yes",
        "disclosure_documents": ["Prospectus", "Product Highlights Sheet", "Fund Fact Sheet"]
    }
    
    return product


# Tool definitions for Gemini function calling
RETIREMENT_TOOLS = [
    {
        "name": "get_investment_options",
        "description": "Get suitable retirement investment options based on user's risk tolerance, investment amount, time horizon, and goals. Returns personalized recommendations with suitability scores.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "risk_tolerance": {
                    "type_": "STRING",
                    "description": "User's risk tolerance level (low, medium, or high)"
                },
                "investment_amount": {
                    "type_": "NUMBER",
                    "description": "Amount available to invest in Malaysian Ringgit (RM)"
                },
                "time_horizon": {
                    "type_": "INTEGER",
                    "description": "Number of years until retirement"
                },
                "goals": {
                    "type_": "ARRAY",
                    "items": {"type_": "STRING"},
                    "description": "Optional list of investment goals"
                }
            },
            "required": ["risk_tolerance", "investment_amount", "time_horizon"]
        }
    },
    {
        "name": "compare_investments",
        "description": "Compare multiple investment products side by side. Shows returns, fees, risk levels, and provides insights on which product performs best in different categories.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "product_ids": {
                    "type_": "ARRAY",
                    "items": {"type_": "STRING"},
                    "description": "List of product IDs to compare (minimum 2). Available IDs: epf, prs_conservative, prs_moderate, prs_growth, unit_trust_equity, unit_trust_balanced, robo_advisor"
                }
            },
            "required": ["product_ids"]
        }
    },
    {
        "name": "calculate_retirement_projection",
        "description": "Calculate detailed retirement savings projection showing future value, real value adjusted for inflation, and estimated monthly income at retirement using the 4% and 3% withdrawal rules.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "current_age": {
                    "type_": "INTEGER",
                    "description": "Current age of the user"
                },
                "retirement_age": {
                    "type_": "INTEGER",
                    "description": "Target retirement age"
                },
                "current_savings": {
                    "type_": "NUMBER",
                    "description": "Current retirement savings in RM"
                },
                "monthly_contribution": {
                    "type_": "NUMBER",
                    "description": "Monthly contribution amount in RM"
                },
                "expected_return": {
                    "type_": "NUMBER",
                    "description": "Expected annual return percentage (e.g., 6.5 for 6.5%)"
                },
                "inflation_rate": {
                    "type_": "NUMBER",
                    "description": "Expected inflation rate percentage (default 3.0)"
                }
            },
            "required": ["current_age", "retirement_age", "current_savings", "monthly_contribution", "expected_return"]
        }
    },
    {
        "name": "get_product_details",
        "description": "Get comprehensive details about a specific investment product including returns, fees, features, regulatory information, and suitability.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "product_id": {
                    "type_": "STRING",
                    "description": "ID of the investment product. Available IDs: epf, prs_conservative, prs_moderate, prs_growth, unit_trust_equity, unit_trust_balanced, robo_advisor"
                }
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "create_investment_order",
        "description": "Create an investment purchase order for a specific product. Returns order details, payment URL, and next steps. User can proceed to payment to complete the investment.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "product_id": {
                    "type_": "STRING",
                    "description": "ID of the investment product to purchase"
                },
                "amount": {
                    "type_": "NUMBER",
                    "description": "Investment amount in RM"
                },
                "user_id": {
                    "type_": "STRING",
                    "description": "User identifier"
                },
                "payment_method": {
                    "type_": "STRING",
                    "description": "Preferred payment method: online_banking, fpx, or credit_card (default: online_banking)"
                }
            },
            "required": ["product_id", "amount", "user_id"]
        }
    },
    {
        "name": "get_user_financial_profile",
        "description": "Retrieve the user's financial profile from their questionnaire responses. Returns occupation, income, expenses, debt, savings, risk tolerance, and personalized analysis including monthly savings capacity and recommendations. Use this to provide personalized advice based on their actual financial situation.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "user_id": {
                    "type_": "STRING",
                    "description": "User identifier"
                }
            },
            "required": ["user_id"]
        }
    }
]


# Function dispatcher for tool execution
TOOL_FUNCTIONS = {
    "get_investment_options": get_investment_options,
    "compare_investments": compare_investments,
    "calculate_retirement_projection": calculate_retirement_projection,
    "get_product_details": get_product_details,
    "create_investment_order": create_investment_order,
    "get_user_financial_profile": get_user_financial_profile,
    "create_epf_topup_action": create_epf_topup_action,
    "create_insurance_recommendation": create_insurance_recommendation,
    "create_savings_goal_action": create_savings_goal_action
}


def execute_tool(tool_name: str, parameters: Dict) -> Dict:
    """
    Execute a retirement planning tool by name.
    
    Args:
        tool_name: Name of the tool to execute
        parameters: Parameters for the tool
    
    Returns:
        Tool execution result
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "error": f"Tool '{tool_name}' not found",
            "available_tools": list(TOOL_FUNCTIONS.keys())
        }
    
    try:
        func = TOOL_FUNCTIONS[tool_name]
        result = func(**parameters)
        return result
    except Exception as e:
        return {
            "error": f"Tool execution failed: {str(e)}",
            "tool": tool_name,
            "parameters": parameters
        }
