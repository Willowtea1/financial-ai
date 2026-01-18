import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List
from services.retirement_tools import execute_tool

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define tools using proper Gemini format
get_investment_options_tool = genai.protos.FunctionDeclaration(
    name="get_investment_options",
    description="Get suitable retirement investment options based on user's risk tolerance, investment amount, time horizon, and goals",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "risk_tolerance": genai.protos.Schema(type=genai.protos.Type.STRING, description="User's risk tolerance level (low, medium, or high)"),
            "investment_amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, description="Amount available to invest in RM"),
            "time_horizon": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="Number of years until retirement"),
        },
        required=["risk_tolerance", "investment_amount", "time_horizon"]
    )
)

compare_investments_tool = genai.protos.FunctionDeclaration(
    name="compare_investments",
    description="Compare multiple investment products side by side with insights on returns, fees, and risk levels",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "product_ids": genai.protos.Schema(
                type=genai.protos.Type.ARRAY,
                items=genai.protos.Schema(type=genai.protos.Type.STRING),
                description="List of product IDs to compare (minimum 2)"
            ),
        },
        required=["product_ids"]
    )
)

calculate_projection_tool = genai.protos.FunctionDeclaration(
    name="calculate_retirement_projection",
    description="Calculate retirement savings projection with future value and monthly income estimates",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "current_age": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="Current age"),
            "retirement_age": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="Target retirement age"),
            "current_savings": genai.protos.Schema(type=genai.protos.Type.NUMBER, description="Current savings in RM"),
            "monthly_contribution": genai.protos.Schema(type=genai.protos.Type.NUMBER, description="Monthly contribution in RM"),
            "expected_return": genai.protos.Schema(type=genai.protos.Type.NUMBER, description="Expected annual return %"),
        },
        required=["current_age", "retirement_age", "current_savings", "monthly_contribution", "expected_return"]
    )
)

get_product_details_tool = genai.protos.FunctionDeclaration(
    name="get_product_details",
    description="Get comprehensive details about a specific investment product",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "product_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="ID of the investment product"),
        },
        required=["product_id"]
    )
)

create_order_tool = genai.protos.FunctionDeclaration(
    name="create_investment_order",
    description="Create an investment purchase order with payment details",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "product_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="Product ID to purchase"),
            "amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, description="Investment amount in RM"),
            "user_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="User identifier"),
        },
        required=["product_id", "amount", "user_id"]
    )
)

get_user_profile_tool = genai.protos.FunctionDeclaration(
    name="get_user_financial_profile",
    description="Retrieve user's financial profile from questionnaire responses including income, expenses, debt, savings, risk tolerance, and personalized analysis. Use this to provide personalized advice based on their actual financial situation.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "user_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="User identifier"),
        },
        required=["user_id"]
    )
)

# Create tool collection
retirement_tools = genai.protos.Tool(
    function_declarations=[
        get_investment_options_tool,
        compare_investments_tool,
        calculate_projection_tool,
        get_product_details_tool,
        create_order_tool,
        get_user_profile_tool
    ]
)

# Initialize the model with tools
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    tools=[retirement_tools]
)

async def generate_financial_plan(user_answers: Dict, context: str):
    """Generate a personalized financial plan using Google Gemini."""
    system_prompt = """You are a certified financial advisor with expertise in personal finance planning for Malaysian residents (RM currency). 
Generate a comprehensive, actionable financial plan based on user responses and relevant financial guidance.

Your response must be a valid JSON object with the following structure:
{
  "situation": "A brief assessment of their current financial situation (2-3 sentences)",
  "priorities": ["Priority 1", "Priority 2", "Priority 3"],
  "roadmap": "A detailed 12-month roadmap with monthly milestones and actionable steps",
  "thisMonthActions": "Specific actions to take this month (detailed and actionable)",
  "longTermStrategy": "Long-term financial strategy and goals (2-3 paragraphs)"
}

Guidelines:
- Use Malaysian Ringgit (RM) currency
- Be specific and actionable
- Consider Malaysian financial context (EPF, taxes, etc.)
- Use markdown formatting (**bold** for emphasis, *italic* for notes)
- Make priorities actionable and measurable
- Reference the provided financial guidance context when relevant"""

    user_prompt = f"""Generate a personalised financial plan for a user with the following profile:

About You: {user_answers.get('aboutYou', 'Not specified')}
Annual Income (RM): {user_answers.get('income', 'Not specified')}
Monthly Expenses (RM): {user_answers.get('expenses', 'Not specified')}
Debt: {user_answers.get('debt', 'Not specified')}
Savings: {user_answers.get('savings', 'Not specified')}
Risk Tolerance: {user_answers.get('riskTolerance', 'Not specified')}

Relevant Financial Guidance Context:
{context}

Generate a comprehensive financial plan that addresses their specific situation, priorities, and provides a clear roadmap for the next 12 months.

Return ONLY valid JSON, no markdown formatting or code blocks."""

    try:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8000,
            )
        )

        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'^```\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        plan = json.loads(response_text)

        # Validate structure
        required_fields = ["situation", "priorities", "roadmap", "thisMonthActions", "longTermStrategy"]
        if not all(field in plan for field in required_fields):
            missing = [f for f in required_fields if f not in plan]
            raise ValueError(f"Invalid plan structure. Missing: {missing}")

        return plan
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response: {str(e)}")
    except Exception as error:
        raise Exception(f"Failed to generate plan: {str(error)}")

async def refine_financial_plan(message: str, plan_data: Dict, chat_history: List[Dict], context: str):
    """Refine financial plan through chat interaction using Google Gemini with function calling."""
    system_prompt = f"""You are a financial advisor assistant helping users refine their financial plan.
You have access to their current financial plan and can answer questions, suggest improvements, or clarify aspects of their plan.

IMPORTANT: You have access to powerful retirement planning tools that you should use when relevant:
- get_investment_options: Find suitable investment products based on risk tolerance and goals
- compare_investments: Compare multiple investment products side by side
- calculate_retirement_projection: Calculate retirement savings projections
- get_product_details: Get detailed information about specific investment products
- create_investment_order: Help users purchase investments directly

When users ask about:
- "What are the best investment options?" → Use get_investment_options
- "Compare these investments" → Use compare_investments
- "How much will I have at retirement?" → Use calculate_retirement_projection
- "Tell me more about [product]" → Use get_product_details
- "I want to invest in [product]" → Use create_investment_order

When responding:
- Be concise and helpful
- Reference specific parts of their plan when relevant
- Use the tools proactively when discussing retirement planning
- If the user asks to modify the plan, provide updated JSON for specific sections
- Use markdown formatting for readability
- If making changes, explain the reasoning

Current Financial Plan:
{json.dumps(plan_data, indent=2)}

Relevant Financial Guidance:
{context}"""

    # Build conversation history
    conversation_parts = [system_prompt]

    # Add chat history (last 10 messages to avoid token limits)
    recent_history = chat_history[-10:] if chat_history else []
    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        conversation_parts.append(f"{role.upper()}: {content}")

    # Add current message
    conversation_parts.append(f"USER: {message}")
    
    conversation = "\n\n".join(conversation_parts)

    try:
        # Start chat with function calling enabled
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        response = chat.send_message(
            conversation,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,
            )
        )

        # Handle function calls
        tool_calls = []
        final_response_text = ""
        
        # Check if model wants to call functions
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # Check if it's a function call
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                tool_name = function_call.name
                
                # Extract parameters
                parameters = {}
                for key, value in function_call.args.items():
                    parameters[key] = value
                
                print(f"[TOOL CALL] {tool_name} with params: {parameters}")
                
                # Execute the tool
                tool_result = execute_tool(tool_name, parameters)
                
                # Store tool call info
                tool_calls.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": tool_result
                })
                
                # Send tool result back to model
                response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_result}
                            )
                        )]
                    )
                )
            else:
                # Regular text response
                if hasattr(part, 'text'):
                    final_response_text = part.text
                break

        # If no text response yet, get it from the response
        if not final_response_text and response.text:
            final_response_text = response.text

        # Try to parse if response contains JSON (for plan updates)
        updated_plan = None
        try:
            json_match = re.search(r'\{[\s\S]*\}', final_response_text)
            if json_match:
                json_text = json_match.group()
                json_text = re.sub(r'^```json\s*', '', json_text)
                json_text = re.sub(r'^```\s*', '', json_text)
                json_text = re.sub(r'\s*```$', '', json_text)
                
                parsed = json.loads(json_text)
                plan_fields = ["situation", "priorities", "roadmap", "thisMonthActions", "longTermStrategy"]
                if any(key in parsed for key in plan_fields):
                    updated_plan = {**plan_data, **parsed}
        except (json.JSONDecodeError, Exception):
            pass

        result = {
            "message": final_response_text,
            "updatedPlan": updated_plan
        }
        
        # Include tool calls if any were made
        if tool_calls:
            result["toolCalls"] = tool_calls

        return result
    except Exception as error:
        print(f"Error in refine_financial_plan: {error}")
        raise Exception(f"Failed to refine plan: {str(error)}")
