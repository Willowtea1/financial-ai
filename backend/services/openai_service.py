import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_financial_plan(user_answers: Dict, context: str):
    """Generate a personalized financial plan using OpenAI."""
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

Generate a comprehensive financial plan that addresses their specific situation, priorities, and provides a clear roadmap for the next 12 months."""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",  # or 'gpt-4o-mini' for cost efficiency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )

        response = completion.choices[0].message.content
        plan = json.loads(response)

        # Validate structure
        required_fields = ["situation", "priorities", "roadmap", "thisMonthActions", "longTermStrategy"]
        if not all(field in plan for field in required_fields):
            raise ValueError("Invalid plan structure from OpenAI")

        return plan
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        raise Exception(f"Failed to parse OpenAI response: {str(e)}")
    except Exception as error:
        print(f"OpenAI API error: {error}")
        raise Exception(f"Failed to generate plan: {str(error)}")

async def refine_financial_plan(message: str, plan_data: Dict, chat_history: List[Dict], context: str):
    """Refine financial plan through chat interaction using OpenAI."""
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
    messages = [{"role": "system", "content": system_prompt}]

    # Add chat history (last 10 messages to avoid token limits)
    recent_history = chat_history[-10:] if chat_history else []
    for msg in recent_history:
        role = msg.get("role", "user")
        # Ensure role is either 'user' or 'assistant'
        if role not in ["user", "assistant"]:
            role = "user" if role == "user" else "assistant"
        messages.append({
            "role": role,
            "content": msg.get("content", "")
        })

    # Add current message
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",  # or 'gpt-4o-mini'
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        response = completion.choices[0].message.content

        # Try to parse if response contains JSON (for plan updates)
        updated_plan = None
        try:
            # Look for JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                parsed = json.loads(json_match.group())
                # Merge with existing plan if it contains plan fields
                plan_fields = ["situation", "priorities", "roadmap", "thisMonthActions", "longTermStrategy"]
                if any(key in parsed for key in plan_fields):
                    updated_plan = {**plan_data, **parsed}
        except (json.JSONDecodeError, Exception) as e:
            # Not JSON, just a text response
            pass

        return {
            "message": response,
            "updatedPlan": updated_plan
        }
    except Exception as error:
        print(f"OpenAI API error: {error}")
        raise Exception(f"Failed to refine plan: {str(error)}")
