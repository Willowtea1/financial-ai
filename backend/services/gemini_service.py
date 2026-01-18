import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-flash')

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
    """Refine financial plan through chat interaction using Google Gemini."""
    system_prompt = f"""You are a financial advisor assistant helping users refine their financial plan.
You have access to their current financial plan and can answer questions, suggest improvements, or clarify aspects of their plan.

When responding:
- Be concise and helpful
- Reference specific parts of their plan when relevant
- If the user asks to modify the plan, provide updated JSON for specific sections
- Use markdown formatting for readability
- If making changes, explain the reasoning

Current Financial Plan:
{json.dumps(plan_data, indent=2)}

Relevant Financial Guidance:
{context}"""

    # Build conversation history
    conversation = system_prompt + "\n\n"

    # Add chat history (last 10 messages to avoid token limits)
    recent_history = chat_history[-10:] if chat_history else []
    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        conversation += f"\n{role.upper()}: {content}\n"

    # Add current message
    conversation += f"\nUSER: {message}\n\nASSISTANT:"

    try:
        response = model.generate_content(
            conversation,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,
            )
        )

        response_text = response.text

        # Try to parse if response contains JSON (for plan updates)
        updated_plan = None
        try:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
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

        return {
            "message": response_text,
            "updatedPlan": updated_plan
        }
    except Exception as error:
        raise Exception(f"Failed to refine plan: {str(error)}")
