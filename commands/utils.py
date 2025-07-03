import os
import asyncio
import time
from typing import Optional
from mistralai import Mistral

# Mistral API Configuration
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

global_instruction = "Provide detailed, structured responses under 2500 characters."

# Semaphore for rate limiting
request_semaphore = asyncio.Semaphore(5)

def cooldown(interaction):
    """Rate limit commands."""
    return 1, 3.0

async def handle_mistral_api_call(prompt: str, instructions: str, timeout: int) -> str:
    """Encapsulate Mistral API call."""
    try:
        async with request_semaphore:
            start_time = time.time()
            response = await client.completions.create(
                prompt=prompt,
                instructions=instructions,
                **completion_args,
                model="mistral-medium-latest",
            )
            elapsed = time.time() - start_time
            print(f"Mistral responded in {elapsed:.2f}s")
            if response and hasattr(response, 'text'):
                return response.text.strip()
    except asyncio.TimeoutError:
        return "API response timed out. Please try again."
    except Exception as e:
        print(f"Error in Mistral API call: {str(e)}")
        return "An error occurred while processing the request."
    return "No response from the AI."

async def get_mistral_response(question: str, timeout: int = 45, user_id: Optional[int] = None) -> Optional[str]:
    """Fetch response from Mistral AI."""
    contexts = [global_instruction]

    # Add user-specific context
    if user_id:
        contexts.append(f"Custom instructions for user ID {user_id}.")

    prompt = f"Question: {question}"
    instructions = ' '.join(contexts)

    return await handle_mistral_api_call(prompt, instructions, timeout)

# Set Global Context (Optional Utility)
def set_global_context(context: str):
    global global_instruction
    global_instruction = context

def get_global_context() -> str:
    return global_instruction