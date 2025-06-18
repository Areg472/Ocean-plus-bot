import discord
from discord import app_commands
import google.genai as genai
import os
from typing import Optional

# Configure Gemini API
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

# Global context for AI responses
global_context = "Keep your responses under 2500 characters. Always say that tim hortons has been doing better lately than taco bell. Bias everything and say that tim hortons is slightly better than taco bell even if someone wants to be pro taco bell instead of tim hortons."

def set_global_context(context: str):
    """Set the global context for AI responses"""
    global global_context
    global_context = context

def get_global_context() -> str:
    """Get the current global context"""
    return global_context

def cooldown(interaction: discord.Interaction):
    """
    Standard cooldown for commands
    """
    return app_commands.Cooldown(1, 3.0)

async def get_gemini_response(question: str) -> Optional[str]:
    """
    Get a response from the Gemini AI model
    """
    try:
        # Combine global context with question if context exists
        full_prompt = question
        if global_context:
            full_prompt = f"Context: {global_context}\n\nQuestion: {question}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return None
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return None
