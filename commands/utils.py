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

async def handle_api_call_stream(prompt: str, instructions: str = "", timeout: int = 45, model: str = "mistral-small-2506", audio_url: Optional[str] = None, rename_audio: bool = False) -> Tuple[str, Optional[str]]:
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
            elif model in ["voxtral-mini-2507", "voxtral-small-2507"]:
                # Handle Voxtral models with audio support
                def sync_voxtral():
                    messages = []
                    if audio_url:
                        # Modify prompt if rename is requested
                        actual_prompt = prompt
                        if rename_audio:
                            actual_prompt = f"{prompt}\n\nAdditionally, based on the audio content, suggest a descriptive filename for this audio file. Format your response as: 'SUGGESTED_FILENAME: [your suggested name]' at the end of your response."
                        
                        # Audio + text message
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_audio",
                                    "input_audio": audio_url,
                                },
                                {
                                    "type": "text",
                                    "text": actual_prompt
                                }
                            ]
                        })
                    else:
                        # Text-only message
                        messages.append({
                            "role": "user",
                            "content": prompt
                        })
                    
                    response = client.chat.complete(
                        model=model,
                        messages=messages
                    )
                    return response.choices[0].message.content if response.choices else "No content received from Voxtral."
                
                response_text = await asyncio.to_thread(sync_voxtral)
                think_text = None
            elif model == "devstral-small-2507":
                if not instructions:
                    instructions = devstral_instruction
                def sync_stream():
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
                    return response_text

                response_text = await asyncio.to_thread(sync_stream)
                think_text = None
            else:
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


async def get_ai_response(
    question: str,
    timeout: int = 45,
    user_id: Optional[int] = None,
    model: str = "mistral-medium-latest",
    audio_url: Optional[str] = None,
    rename_audio: bool = False
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
        answer, think_text = await handle_api_call_stream(question, instructions, timeout, model, audio_url, rename_audio)
        return answer, think_text
    else:
        return await handle_api_call_stream(question, instructions, timeout, model, audio_url, rename_audio)


def set_global_context(context: str):
    global global_instruction
    global_instruction = context


def get_global_context() -> str:
    return global_instruction