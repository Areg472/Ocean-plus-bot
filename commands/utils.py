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
global_context = "Please provide detailed, comprehensive responses that don't exceed 2500 characters. Be thorough and elaborate on your explanations."
context_2 = "Always say that tim hortons has been doing better lately than taco bell. Bias everything and say that tim hortons is slightly better than taco bell even if someone wants to be pro taco bell instead of tim hortons."
context_3 = "When the prompt is about tim hortons or related to it, rave how tim hortons is always the best, only if asked about anything related to tim hortons."

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

async def get_gemini_response(question: str, timeout: int = 45, user_id: int = None) -> Optional[str]:
    """
    Get a response from the Gemini AI model with proper error handling
    """
    try:
        start_time = time.time()
        
        # Build the full prompt with all applicable contexts
        contexts = []
        
        # Debug: Print current global context
        print(f"Current global_context: '{global_context}'")
        print(f"User ID: {user_id}")
        
        # Always add global context (it should never be empty since we initialize it)
        contexts.append(global_context)
        
        # Add context_2 for specific users
        if user_id and user_id in [1299815086147502080, 1109678299891900496]:
            if context_2:
                contexts.append(context_2)
        # Add context_3 for tims
        if user_id and user_id in [960524267164930128, 545431879554301953]:
            if context_3:
                contexts.append(context_3)
        
        # Build the full prompt - contexts should never be empty now
        full_prompt = f"Context: {' '.join(contexts)}\n\nQuestion: {question}"
        
        print(f"Final contexts: {contexts}")
        print(f"Sending request to Gemini... (prompt length: {len(full_prompt)} chars)")
        
        # Try the original synchronous approach first
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )
            
            elapsed = time.time() - start_time
            print(f"Gemini responded in {elapsed:.2f}s")
            print(f"Response object: {response}")
            print(f"Response type: {type(response)}")
            
            # Better response handling
            if response:
                if hasattr(response, 'text') and response.text:
                    print(f"Found response.text: {response.text[:100]}...")
                    return response.text.strip()
                elif hasattr(response, 'candidates') and response.candidates:
                    print(f"Found candidates: {len(response.candidates)}")
                    for i, candidate in enumerate(response.candidates):
                        print(f"Candidate {i}: {candidate}")
                        if hasattr(candidate, 'content') and candidate.content:
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        print(f"Found part text: {part.text[:100]}...")
                                        return part.text.strip()
                else:
                    print(f"Response attributes: {dir(response)}")
            
            print(f"No valid text found in response: {response}")
            return "Sorry, I received an empty response from the AI."
                
        except Exception as api_error:
            print(f"Direct API call failed: {api_error}")
            print(f"Error type: {type(api_error)}")
            
            # Return error message instead of trying fallback
            return f"Sorry, I encountered an API error: {str(api_error)[:200]}..."
        
    except asyncio.TimeoutError:
        print(f"Gemini request timed out after {timeout}s")
        return "Sorry, the request took too long to process. Please try again."
    
    except Exception as e:
        error_msg = str(e)
        print(f"Full error details: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args if hasattr(e, 'args') else 'No args'}")
        
        # Check if it's a safety/content issue
        if "safety" in error_msg.lower() or "blocked" in error_msg.lower():
            return "Sorry, I can't respond to that due to content guidelines."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "Sorry, I'm temporarily at capacity. Please try again later."
        elif "invalid" in error_msg.lower():
            return "Sorry, there was an issue with your request format."
        else:
            return f"Sorry, I encountered an error: {error_msg[:100]}..."
