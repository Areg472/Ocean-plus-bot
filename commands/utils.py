import discord
from discord import app_commands
import google.generativeai as genai
import os
from typing import Optional

# Configure Gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize user history for chat
user_history = {}
MAX_HISTORY = 30

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
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return None
