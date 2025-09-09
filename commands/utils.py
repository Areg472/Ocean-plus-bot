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
            elif model in ["magistral-small-2507", "magistral-medium-2507"]:
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
            elif model in [
                "mistral-small-2506","mistral-medium-2508","gpt-5-nano",
                "gpt-5-mini","gpt-5","gpt-4.1","gpt-4.1-mini","gpt-4.1-nano",
                "o4-mini"
            ] and (image_url or image_urls):
                def sync_image():
                    if model.startswith("gpt-") or model == "o4-mini":
                        content = [{"type": "input_text", "text": prompt}]
                        
                        if image_urls:
                            content.extend({"type": "input_image", "image_url": url} for url in image_urls)
                        elif image_url:
                            content.append({"type": "input_image", "image_url": image_url})
                        
                        response = openAI_client.responses.create(
                            model=model,
                            input=[{
                                "role": "user",
                                "content": content
                            }],
                            service_tier="flex",
                            reasoning={
                                "effort": "medium",
                                "summary": "auto"
                            } if model in ["gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"] else None
                        )
                        return response
                    else:
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
                        return response
                
                response = await asyncio.to_thread(sync_image)

                if model.startswith("gpt-5") or model == "o4-mini":
                    print(response)
                    response_text = response.output[0].content[0].text if response.output and response.output[0].content else "No content received from GPT."
                    think_text = None
                    if model in ["gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"] and hasattr(response, 'reasoning') and response.reasoning and hasattr(response.reasoning, 'summary') and response.reasoning.summary:
                        think_text = response.reasoning.summary
                    return response_text, think_text
                elif model.startswith("gpt-4"):
                    print(response)
                    response_text = response.output[0].content[0].text if response.output and response.output[0].content else "No content received from GPT."
                    think_text = None
                    return response_text, think_text
                else:
                    response_text = response.choices[0].message.content if response.choices else "No content received from Mistral."
                    think_text = None
            elif model in [
                "gpt-5-nano","gpt-5-mini","gpt-5","gpt-4.1","gpt-4.1-mini",
                "gpt-4.1-nano","o4-mini"
            ]:
                def sync_gpt():
                    if model.startswith("gpt-5") or model == "o4-mini":
                        content = [{"type": "input_text", "text": prompt}]
                        
                        if image_url:
                            content.append({"type": "input_image", "image_url": image_url})
                        if image_urls:
                            content.extend({"type": "input_image", "image_url": url} for url in image_urls)
                        
                        response = openAI_client.responses.create(
                            model=model,
                            input=[{
                                "role": "user",
                                "content": content
                            }],
                            service_tier="flex",
                            reasoning={
                                "effort": "medium",
                                "summary": "auto"
                            } if model in ["gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"] else None
                        )
                        return response
                    else:
                        content = [{"type": "input_text", "text": prompt}]
                        
                        response = openAI_client.responses.create(
                            model=model,
                            input=[{
                                "role": "user",
                                "content": content
                            }],
                        )
                        return response

                response = await asyncio.to_thread(sync_gpt)
                print(response)
                
                response_text = response.output[0].content[0].text if response.output and response.output[0].content else "No content received from GPT."
                think_text = None
                if model in ["gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"] and hasattr(response, 'reasoning') and response.reasoning and hasattr(response.reasoning, 'summary') and response.reasoning.summary:
                    think_text = response.reasoning.summary
                return response_text, think_text
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

            if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"]:
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
    model: str = "mistral-small-2506",
    audio_url: Optional[str] = None,
    image_url: Optional[str] = None,
    image_urls: Optional[list] = None,
    instructions: str = "",
    input_limit: bool = False
) -> Optional[str]:

    if input_limit and len(question) > 3000:
        error_msg = "Input exceeds the 3000 character limit. Please shorten your message."
        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"]:
            return error_msg, None
        else:
            return error_msg

    contexts = [global_instruction]
    if instructions:
        contexts.append(instructions)
    final_instructions = ' '.join(contexts)

    if await moderate_content(question, audio_url):
        error_msg = "Your message has been flagged by our content moderation system lol(OpenAI model btw). Please revise your input."
        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"]:
            return error_msg, None
        else:
            return error_msg

    result = await handle_api_call_stream(question, final_instructions, timeout, model, audio_url, image_url, image_urls)
    
    if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "gpt-5-nano", "gpt-5-mini", "gpt-5", "o4-mini"]:
        return result
    else:
        return result[0] if isinstance(result, tuple) else result 


def set_global_context(context: str):
    global global_instruction
    global_instruction = context


def get_global_context() -> str:
    return global_instruction

async def moderate_content(content: str, audio_url: Optional[str] = None) -> bool:
    if audio_url:
        return False
    
    try:
        def sync_moderate():
            response = openAI_client.moderations.create(
                model="omni-moderation-latest",
                input=content
            )
            return response.results[0].flagged
        
        return await asyncio.to_thread(sync_moderate)
    except Exception as e:
        print(f"Moderation error: {e}")
        return False