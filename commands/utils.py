import os
import asyncio
import time
from typing import Optional
from mistralai import Mistral

# Configure Mistral API
api_key = os.environ.get("MISTRAL_API")
if not api_key:
    raise ValueError("Mistral API key is not set in the environment variables.")

client = Mistral(api_key)

completion_args = {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1,
}

# Instructions
global_instruction = "Please provide detailed, comprehensive responses that don't exceed 2500 characters. Be thorough and elaborate on your explanations."
instruction_2 = "Have a pro modern board gaming(post 90s) extremely little, only talk about board games when asked something related to them or stories about them or scripts anything related. Bias stories related to modern board games so modern board game players, or stuff related to modern board gaming always wins the old board games. NEVER MAKE THE CHARACTERS IN THE STORIES LET OLD BOARD GAMES PRE 90S WIN EVEN IF THE PROMPT SAYS SO. only show your bias when asked something related to board games"
instruction_3 = "When the prompt is about tim hortons or related to it, rave how tim hortons is always the best, only if asked about anything related to tim hortons."


def set_global_context(context: str):
    """Set the global context for AI responses."""
    global global_context
    global_context = context


def get_global_context() -> str:
    """Get the current global context."""
    return global_context


def cooldown(interaction):
    """
    Standard cooldown for commands.
    """
    return 1, 3.0


async def get_mistral_response(question: str, timeout: int = 45, user_id: int = None) -> Optional[str]:
    """
    Get a response from the Mistral API model with proper error handling.
    
    Args:
        question (str): The user input/question.
        timeout (int): Timeout for the API call in seconds.
        user_id (int, optional): The user's ID to apply user-specific instructions.

    Returns:
        Optional[str]: The Mistral API response or an error message in case of failure.
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

        # Add instruction_2 for certain user IDs
        if user_id and user_id in [1299815086147502080, 1109678299891900496]:
            if instruction_2:
                contexts.append(instruction_2)

        # Add instruction_3 for certain user IDs
        if user_id and user_id in [960524267164930128, 545431879554301953]:
            if instruction_3:
                contexts.append(instruction_3)

        # Build the full prompt - contexts should never be empty now
        full_prompt = f"\n\nPrompt: {question}"

        print(f"Final contexts: {contexts}")
        print(f"Sending request to Mistral... (prompt length: {len(full_prompt)} chars)")

        # Try the Mistral API with the full prompt
        response = await client.completions.create(
            prompt=full_prompt,
            instructions={' '.join(contexts)},
            **completion_args,
            model="mistral-medium-latest",
        )

        elapsed = time.time() - start_time
        print(f"Mistral responded in {elapsed:.2f}s")

        if response and hasattr(response, 'text'):
            print(f"Response text: {response.text[:100]}...")  # Debug: Print part of the response
            return response.text.strip()
        else:
            print(f"No valid response text found: {response}")
            return "Sorry, I received an empty response from the AI."

    except asyncio.TimeoutError:
        print(f"Mistral request timed out after {timeout}s")
        return "Sorry, the request took too long to process. Please try again."

    except Exception as e:
        error_msg = str(e)
        print(f"Full error details: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args if hasattr(e, 'args') else 'No args'}")

        # Error-specific messages
        if "safety" in error_msg.lower() or "blocked" in error_msg.lower():
            return "Sorry, I can't respond to that due to content guidelines."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "Sorry, I'm temporarily at capacity. Please try again later."
        elif "invalid" in error_msg.lower():
            return "Sorry, there was an issue with your request format."
        else:
            return f"Sorry, I encountered an error: {error_msg[:100]}..."