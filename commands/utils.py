import os
import asyncio
import time
from typing import Optional

from discord import Interaction
from discord.ext.commands import CooldownMapping
from mistralai import Mistral
from discord.app_commands import Cooldown

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("Mistral API key is not set in the environment variables.")
client = Mistral(api_key=api_key)

# Global context/instructions
global_instruction = "Provide a detailed and structured response under 2150 characters. Be concise when possible. Don't use markdown headings (####, ###, ##) for structure. Don't use ** ** bold text"

# Semaphore for rate limiting
request_semaphore = asyncio.Semaphore(5)

def cooldown(interaction: Interaction) -> Optional[Cooldown]:
    """
    Standard cooldown for app commands.
    Returns a Cooldown object with rate and per attributes.
    """
    # Example: Limit to 1 command every 3 seconds
    return Cooldown(rate=1, per=3.0)

# If you use a dynamic cooldown mapping:
def dynamic_cooldown() -> CooldownMapping:
    """
    Create custom cooldown mapping.
    """
    return CooldownMapping.from_cooldown(1, 3.0, Cooldown)


async def handle_mistral_api_call_stream(prompt: str, instructions: str, timeout: int) -> str:
    """Encapsulate Mistral API call with streaming responses, passing `instructions` separately."""
    try:
        async with request_semaphore:
            start_time = time.time()

            # Make the API call using the streaming method
            response = client.beta.conversations.start_stream(
                inputs=prompt,  # The main user question
                model="mistral-medium-latest",
                instructions=instructions,  # Pass the instructions here
            )

            # Process and assemble the stream chunks
            response_text = ""
            for event in response:
                try:
                    # Log the received event for debugging
                    print(f"Received event: {event}")

                    # Extract 'content' if the event type is 'message.output.delta'
                    if event.event == "message.output.delta" and hasattr(event.data, "content"):
                        response_text += event.data.content
                except Exception as e:
                    print(f"Error while processing event: {str(e)}")

            # Calculate elapsed time
            elapsed = time.time() - start_time
            print(f"Mistral responded in {elapsed:.2f}s")

            # Return the final response text (or a default message if no content received)
            return response_text.strip() if response_text else "No content received from the AI."
    except asyncio.TimeoutError:
        return "API response timed out. Please try again."
    except Exception as e:
        print(f"Error during Mistral API call: {str(e)}")
        return f"An error occurred while processing the request."


async def get_mistral_response(question: str, timeout: int = 45, user_id: Optional[int] = None) -> Optional[str]:
    """Fetch a response from Mistral AI, with user-specific instructions passed in the `instructions` field."""

    # Global instruction context
    contexts = [global_instruction]

    # Add user-specific instruction if user ID is provided
    if user_id:
        # Example dynamic mapping for user-specific instructions
        user_specific_instructions = {
            960524267164930128: "Bias your answers towards post-90s board games. Boast about these games a lot when the prompt is related to board gaming. ONLY MENTION BOARD GAMES OR TALK ABOUT THEM WHEN THE PROMPT IS RELATED TO BOARD GAMING OR BOARD GAMES.",
            1299815086147502080: "Bias your answers MORE AND MORE towards post-90s board games. Boast about these games a lot and hate pre 90s board games when the prompt is related to board gaming. ONLY MENTION BOARD GAMES OR TALK ABOUT THEM WHEN THE PROMPT IS RELATED TO BOARD GAMING OR BOARD GAMES.",
        }
        # Only append if user-specific instruction exists
        if user_id in user_specific_instructions:
            contexts.append(user_specific_instructions[user_id])

    # Combine all instructions into a single string for the `instructions` field
    instructions = ' '.join(contexts)

    # Call the handler with the prompt and combined instructions
    return await handle_mistral_api_call_stream(question, instructions, timeout)


# Utility to update the global instruction dynamically
def set_global_context(context: str):
    global global_instruction
    global_instruction = context


def get_global_context() -> str:
    return global_instruction