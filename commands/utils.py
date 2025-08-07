import os
import asyncio
import time
from typing import Optional, Tuple

from discord import Interaction
from discord.ext.commands import CooldownMapping
from mistralai import Mistral
from discord.app_commands import Cooldown
from together import Together
from openai import OpenAI

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("Mistral API key is not set in the environment variables.")

client = Mistral(api_key=api_key)
openAI_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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

async def handle_api_call_stream(prompt: str, instructions: str = "", timeout: int = 45, model: str = "mistral-small-2506", audio_url: Optional[str] = None, image_url: Optional[str] = None, image_urls: Optional[list] = None) -> Tuple[str, Optional[str]]:
    try:
        async with request_semaphore:
            start_time = time.time()

            if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "openai/gpt-oss-120b"]:
                def sync_together():
                    response = together_client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": instructions},{"role": "user", "content": prompt}]
                    )
                    print(response);
                    content = response.choices[0].message.content if response.choices else "No content received from Together AI."
                    if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput"]:
                        import re
                        think_match = re.search(r"<think>(.*?)</think>", content, flags=re.DOTALL)
                        think_text = think_match.group(1).strip() if think_match else None
                        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
                        return content, think_text
                    elif model == "openai/gpt-oss-120b":
                        think_text = response.choices[0].message.reasoning if response.choices and hasattr(response.choices[0].message, 'reasoning') else None
                        return content, think_text
                    return content
                response = await asyncio.to_thread(sync_together)
                if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "openai/gpt-oss-120b"]:
                    response_text, think_text = response
                else:
                    response_text = response
                    think_text = None
            elif model in ["voxtral-mini-2507", "voxtral-small-2507"]:
                def sync_voxtral():
                    messages = []
                    if audio_url:
                        messages.append(
                            {
                                "role": "system",
                                "content": instructions,
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                    "type": "input_audio",
                                    "input_audio": audio_url,
                                },
                                {
                                    "type": "text",
                                    "text": prompt,
                                }
                            ]
                        })
                    else:
                        return "Voxtral models require an audio file."
                    
                    response = client.chat.complete(
                        model=model,
                        messages=messages
                    )
                    return response.choices[0].message.content if response.choices else "No content received from Voxtral."
                
                response_text = await asyncio.to_thread(sync_voxtral)
                think_text = None
            elif model in ["devstral-small-2507", "magistral-small-2507", "magistral-medium-2507"]:
                if not instructions:
                    instructions = devstral_instruction
                def sync_stream():
                    messages = [
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": prompt}
                    ]  

                    response = client.chat.complete(
                        messages=messages,
                        model=model,
                    )
                    print(response)
                    
                    if model in ["magistral-small-2507", "magistral-medium-2507"] and response.choices:
                        content = response.choices[0].message.content
                        if isinstance(content, list):
                            think_text = None
                            response_text = ""
                            
                            for chunk in content:
                                if hasattr(chunk, 'type') and chunk.type == 'thinking':
                                    if hasattr(chunk, 'thinking') and chunk.thinking:
                                        think_text = chunk.thinking[0].text if chunk.thinking else None
                                elif hasattr(chunk, 'type') and chunk.type == 'text':
                                    response_text = chunk.text
                            
                            return response_text, think_text
                        else:
                            return content if content else "No content received from Magistral.", None
                    else:
                        return response.choices[0].message.content if response.choices else "No content received from Mistral.", None

                response_text, think_text = await asyncio.to_thread(sync_stream)
            elif model in ["mistral-small-2506", "mistral-medium-2505"] and (image_url or image_urls):
                def sync_image():
                    content = [{"type": "text", "text": prompt}]
                    
                    if image_urls:
                        for img_url in image_urls:
                            content.append({"type": "image_url", "image_url": img_url})
                    elif image_url:
                        content.append({"type": "image_url", "image_url": image_url})
                    
                    messages = [
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": content}
                        ]
                    
                    response = client.chat.complete(
                        model=model,
                        messages=messages
                    )
                    return response.choices[0].message.content if response.choices else "No content received from Mistral."
                
                response_text = await asyncio.to_thread(sync_image)
                think_text = None
            elif model in ["gpt-5-nano", "gpt-5-mini"]:
                if model in ["gpt-5-mini"]:
                    response = openAI_client.responses.create(
                        model=model,
                        input=prompt,
                        instructions=instructions,
                        service_tier="flex",
                        reasoning={
                            "effort": "medium",
                            "summary": "auto"
                        }
                    )
                else:
                    response = openAI_client.responses.create(
                        model=model,
                        input=prompt,
                        instructions=instructions,
                        reasoning={
                            "effort": "medium",
                            "summary": "auto"
                        }
                    )
            
                print(response)
                response_text = response.output[1].content[0].text if response.output and len(response.output) > 1 and response.output[1].content else "No content received from GPT-5-mini."
                think_text = None
            else:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ]  

                response = client.chat.complete(
                    messages=messages,
                    model=model,
                )
                print(response)
                response_text = response.choices[0].message.content if response.choices else "No content received from Mistral."
                think_text = None

            elapsed = time.time() - start_time
            print(f"The API provider for AI responded in {elapsed:.2f}s")

            if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b"]:
                return response_text.strip() if response_text else "No content received from the AI.", think_text
            else:
                return response_text.strip() if response_text else "No content received from the AI.", None
    except asyncio.TimeoutError:
        return "API response timed out. Please try again.", None
    except Exception as e:
        print(f"Error during AI API call: {str(e)}")
        return f"An error occurred while processing the request.", None


async def get_ai_response(
    question: str,
    timeout: int = 45,
    user_id: Optional[int] = None,
    model: str = "mistral-small-2506",
    audio_url: Optional[str] = None,
    image_url: Optional[str] = None,
    image_urls: Optional[list] = None
) -> Optional[str]:

    if model in ["devstral-small-2507", "magistral-small-2507", "magistral-medium-2507"]:
        contexts = [devstral_instruction]
        instructions = devstral_instruction
    else:
        contexts = [global_instruction]
        if user_id:
            user_specific_instructions = {
            }
            if user_id in user_specific_instructions:
                contexts.append(user_specific_instructions[user_id])
        instructions = ' '.join(contexts)

    result = await handle_api_call_stream(question, instructions, timeout, model, audio_url, image_url, image_urls)
    
    if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b"]:
        return result  
    else:
        return result[0] if isinstance(result, tuple) else result 


def set_global_context(context: str):
    global global_instruction
    global_instruction = context


def get_global_context() -> str:
    return global_instruction