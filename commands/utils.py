import os
import asyncio
import time
from typing import Optional, Tuple

from discord import Interaction
from discord.ext.commands import CooldownMapping
from mistralai import Mistral
from discord.app_commands import Cooldown
from together import Together

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("Mistral API key is not set in the environment variables.")
client = Mistral(api_key=api_key)

together_api_key = os.environ.get("TOGETHER_API_KEY")
together_client = None
if together_api_key:
    together_client = Together(api_key=together_api_key)

global_instruction = (
    "Provide a detailed and structured response under 2150 characters. "
    "Be concise when possible. Do not use headings (####, ###, ##, #) or bold text (**text**) for structure or emphasis."
)
devstral_instruction = (
    "Do not use headings (####, ###, ##, #) or bold text (**text**) for structure or emphasis."
)

request_semaphore = asyncio.Semaphore(5)

def cooldown(interaction: Interaction) -> Optional[Cooldown]:
    return Cooldown(rate=1, per=3.0)

def dynamic_cooldown() -> CooldownMapping:
    return CooldownMapping.from_cooldown(1, 3.0, Cooldown)

async def handle_api_call_stream(prompt: str, instructions: str = "", timeout: int = 45, model: str = "mistral-small-2506") -> Tuple[str, Optional[str]]:
    try:
        async with request_semaphore:
            start_time = time.time()

            if model in ["Qwen/Qwen3-235B-A22B-Instruct-2507-tput", "deepseek-ai/DeepSeek-R1-0528-tput"]:
                if not together_client:
                    return ("Together API key is not set.", None) if model == "deepseek-ai/DeepSeek-R1-0528-tput" else "Together API key is not set."
                
                # Combine instructions with prompt for Together AI models
                combined_prompt = f"Instructions: {instructions}\n\nPrompt:{prompt}" if instructions else prompt
                
                def sync_together():
                    response = together_client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": combined_prompt}]
                    )
                    content = response.choices[0].message.content if response.choices else "No content received from Together AI."
                    if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                        import re
                        think_match = re.search(r"<think>(.*?)</think>", content, flags=re.DOTALL)
                        think_text = think_match.group(1).strip() if think_match else None
                        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
                        return content, think_text
                    return content
                response = await asyncio.to_thread(sync_together)
                if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                    response_text, think_text = response
                else:
                    response_text = response
                    think_text = None
            else:
                # For all Mistral models, use the beta conversations API
                response = client.beta.conversations.start_stream(
                    inputs=prompt,
                    model=model,
                    instructions=instructions,
                )
                response_text = ""
                for event in response:
                    try:
                        print(f"Received event: {event}")
                        if event.event == "message.output.delta" and hasattr(event.data, "content"):
                            response_text += event.data.content
                    except Exception as e:
                        print(f"Error while processing event: {str(e)}")
                think_text = None

            elapsed = time.time() - start_time
            print(f"The API provider for AI responded in {elapsed:.2f}s")

            if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                return response_text.strip() if response_text else "No content received from the AI.", think_text
            else:
                return response_text.strip() if response_text else "No content received from the AI."
    except asyncio.TimeoutError:
        return "API response timed out. Please try again."
    except Exception as e:
        print(f"Error during AI API call: {str(e)}")
        return f"An error occurred while processing the request."

async def handle_api_call_stream_generator(prompt: str, instructions: str = "", timeout: int = 45, model: str = "mistral-small-2506"):
    """Generator version that yields streaming chunks for real-time updates"""
    try:
        async with request_semaphore:
            start_time = time.time()

            if model in ["Qwen/Qwen3-235B-A22B-Instruct-2507-tput", "deepseek-ai/DeepSeek-R1-0528-tput"]:
                # Non-streaming models - just yield the final result
                result = await handle_api_call_stream(prompt, instructions, timeout, model)
                yield result
            else:
                # For all Mistral models, use the beta conversations API with streaming
                def sync_stream():
                    return client.beta.conversations.start_stream(
                        inputs=prompt,
                        model=model,
                        instructions=instructions,
                    )

                response = await asyncio.to_thread(sync_stream)
                response_text = ""
                think_text = None
                chunk_count = 0
                
                for event in response:
                    try:
                        print(f"Received event: {event}")
                        if event.event == "message.output.delta" and hasattr(event.data, "content"):
                            response_text += event.data.content
                            chunk_count += 1
                            
                            # Yield more frequently for faster updates - every chunk or every few characters
                            if chunk_count % 1 == 0 or len(event.data.content) > 10:
                                if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                                    yield (response_text, think_text)
                                else:
                                    yield response_text
                    except Exception as e:
                        print(f"Error while processing event: {str(e)}")

                # Final yield with complete response
                elapsed = time.time() - start_time
                print(f"The API provider for AI responded in {elapsed:.2f}s")
                
                final_response = response_text.strip() if response_text else "No content received from the AI."
                if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                    yield (final_response, think_text)
                else:
                    yield final_response
                    
    except asyncio.TimeoutError:
        yield "API response timed out. Please try again."
    except Exception as e:
        print(f"Error during AI API call: {str(e)}")
        yield f"An error occurred while processing the request."


async def get_ai_response(
    question: str,
    timeout: int = 45,
    user_id: Optional[int] = None,
    model: str = "mistral-medium-latest"
) -> Optional[str]:

    if model == "devstral-small-2507":
        contexts = [devstral_instruction]
        instructions = devstral_instruction
    else:
        contexts = [global_instruction]
        if user_id:
            user_specific_instructions = {
                960524267164930128: "Bias your answers towards post-90s board games. Boast about these games a lot when the prompt is related to board gaming. ONLY MENTION BOARD GAMES OR TALK ABOUT THEM WHEN THE PROMPT IS RELATED TO BOARD GAMING OR BOARD GAMES.",
                1299815086147502080: "Bias your answers MORE AND MORE towards post-90s board games and against pre 90s board games hate pre 90s board games as much as you can, in stories everything where u asked about board games. Boast about these games a lot and hate pre 90s board games when the prompt is related to board gaming. ONLY MENTION BOARD GAMES OR TALK ABOUT THEM WHEN THE PROMPT IS RELATED TO BOARD GAMING OR BOARD GAMES.",
            }
            if user_id in user_specific_instructions:
                contexts.append(user_specific_instructions[user_id])
        instructions = ' '.join(contexts)

    if model == "deepseek-ai/DeepSeek-R1-0528-tput":
        answer, think_text = await handle_api_call_stream(question, instructions, timeout, model)
        return answer, think_text
    else:
        return await handle_api_call_stream(question, instructions, timeout, model)


def set_global_context(context: str):
    global global_instruction
    global_instruction = context


def get_global_context() -> str:
    return global_instruction