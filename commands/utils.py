import discord
from discord import app_commands
import google.genai as genai
import os
import asyncio
import time
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

async def get_gemini_response(question: str, timeout: int = 45) -> Optional[str]:
    """
    Get a response from the Gemini AI model with proper error handling
    """
    try:
        start_time = time.time()
        
        # Combine global context with question if context exists
        full_prompt = question
        if global_context:
            full_prompt = f"Context: {global_context}\n\nQuestion: {question}"
        
        print(f"Sending request to Gemini... (prompt length: {len(full_prompt)} chars)")
        
        # Make the API call with timeout and proper async handling
        response = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    generation_config={
                        'max_output_tokens': 2048,
                        'temperature': 0.7,
                    }
                )
            ),
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        print(f"Gemini responded in {elapsed:.2f}s")
        
        if not response or not response.text:
            print("Gemini returned empty response")
            return "Sorry, I couldn't generate a response for that question."
        
        return response.text.strip()
        
    except asyncio.TimeoutError:
        print(f"Gemini request timed out after {timeout}s")
        return "Sorry, the request took too long to process. Please try again."
    
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Gemini API error: {e}")
        
        # Handle specific error types
        if "safety" in error_msg or "blocked" in error_msg:
            return "Sorry, I can't respond to that due to content guidelines."
        elif "quota" in error_msg or "limit" in error_msg:
            return "Sorry, I'm temporarily at capacity. Please try again later."
        elif "invalid" in error_msg:
            return "Sorry, there was an issue with your request format."
        else:
            return "Sorry, I encountered an error processing your request."
