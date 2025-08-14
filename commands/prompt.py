import discord
from discord import app_commands
from commands.utils import cooldown, get_ai_response
import asyncio
import re


class MediaSelectionView(discord.ui.View):
    def __init__(self, query: str, model: str, audio: discord.Attachment, images: list, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.query = query
        self.model = model
        self.audio = audio
        self.images = images
        self.original_interaction = interaction

    @discord.ui.button(label="Use Audio", style=discord.ButtonStyle.secondary, emoji="🎵")
    async def use_audio(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.process_prompt(interaction, use_audio=True)

    @discord.ui.button(label="Use Images", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def use_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.process_prompt(interaction, use_audio=False)

    async def process_prompt(self, interaction: discord.Interaction, use_audio: bool):
        if use_audio:
            model = "voxtral-mini-2507" if self.model not in ["voxtral-mini-2507", "voxtral-small-2507"] else self.model
            model_name = "Voxtral Mini" if model == "voxtral-mini-2507" else "Voxtral Small"
            media_description = f"📎 {self.audio.filename}"
        else:
            model = "mistral-small-2506" if self.model not in ["mistral-small-2506", "mistral-medium-2508", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini"] else self.model
            if model == "mistral-small-2506":
                model_name = "Mistral Small"
            elif model == "mistral-medium-2508":
                model_name = "Mistral Medium"
            elif model == "gpt-5-nano":
                model_name = "GPT 5 Nano"
            elif model == "gpt-5-mini":
                model_name = "GPT 5 Mini"
            elif model == "gpt-5":
                model_name = "GPT 5"
            elif model == "gpt-4.1":
                model_name = "GPT 4.1"
            elif model == "gpt-4.1-mini":
                model_name = "GPT 4.1 Mini"
            elif model == "gpt-4.1-nano":
                model_name = "GPT 4.1 Nano"
            elif model == "o4-mini":
                model_name = "GPT o4 Mini"
            image_names = [img.filename for img in self.images]
            media_description = f"🖼️ {', '.join(image_names)}"

        thinking_embed = discord.Embed(
            title="🤔 Thinking...",
            description=f"Processing your prompt with {model_name}...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="Prompt", value=self.query[:1000], inline=False)
        thinking_embed.add_field(name="Media Files", value=f"{media_description} (using {model_name})", inline=False)

        await interaction.edit_original_response(embed=thinking_embed)

        try:
            if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "o4-mini", "gpt-5-nano", "gpt-5-mini", "gpt-5"]:
                answer, think_text = await asyncio.wait_for(
                    get_ai_response(self.query, user_id=self.original_interaction.user.id, model=model, 
                                  audio_url=self.audio.url if use_audio else None,
                                  image_urls=[img.url for img in self.images] if not use_audio else None), timeout=360
                )
            else:
                answer = await asyncio.wait_for(
                    get_ai_response(self.query, user_id=self.original_interaction.user.id, model=model,
                                  audio_url=self.audio.url if use_audio else None,
                                  image_urls=[img.url for img in self.images] if not use_audio else None), timeout=60
                )
                think_text = None
        except asyncio.TimeoutError:
            answer = "Sorry, the AI took too long. Try again with a simpler question."
            think_text = None
        except Exception as error:
            answer = f"An error occurred: {error}"
            think_text = None

        response_embed = discord.Embed(title="💡 Output", color=0x34a853)
        response_embed.add_field(name="Prompt", value=self.query[:1000], inline=False)
        
        if use_audio:
            response_embed.add_field(name="Audio File", value=f"[{self.audio.filename}]({self.audio.url})", inline=False)
        else:
            image_links = [f"[{img.filename}]({img.url})" for img in self.images]
            response_embed.add_field(name="Image Files", value="\n".join(image_links), inline=False)

        if len(answer) > 1024:
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
        else:
            response_embed.add_field(name="Answer", value=answer, inline=False)

        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "o4-mini", "gpt-5-nano", "gpt-5-mini", "gpt-5"] and think_text:
            view = ThinkingButtonView(think_text)
            await interaction.edit_original_response(embed=response_embed, view=view)
        else:
            await interaction.edit_original_response(embed=response_embed)


class ThinkingButtonView(discord.ui.View):
    def __init__(self, thinking_text: str):
        super().__init__(timeout=180)
        self.thinking_text = thinking_text

    @discord.ui.button(label="Show Thinking Output", style=discord.ButtonStyle.secondary)
    async def show_thinking(self, interaction: discord.Interaction, button: discord.ui.Button):
        max_content_per_embed = 5800
        
        
        if len(self.thinking_text) <= max_content_per_embed:
            chunks = [self.thinking_text[i:i+1024] for i in range(0, len(self.thinking_text), 1024)]
            embed = discord.Embed(title="Thinking Output", color=0x4285f4)
            
            max_fields = min(len(chunks), 25)
            for idx in range(max_fields):
                chunk = chunks[idx]
                field_name = f"Output Part {idx + 1}" if max_fields > 1 else "Output"
                embed.add_field(name=field_name, value=chunk, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Thinking output is very large. Sending in multiple messages...", ephemeral=True)
            
            
            text_chunks = []
            start = 0
            while start < len(self.thinking_text):
                end = min(start + max_content_per_embed, len(self.thinking_text))
                text_chunks.append(self.thinking_text[start:end])
                start = end
            
            for i, text_chunk in enumerate(text_chunks):
                chunks = [text_chunk[j:j+1024] for j in range(0, len(text_chunk), 1024)]
                embed = discord.Embed(
                    title=f"Thinking Output (Part {i + 1}/{len(text_chunks)}",
                    color=0x4285f4
                )
                
                max_fields = min(len(chunks), 25)
                for idx in range(max_fields):
                    chunk = chunks[idx]
                    field_name = f"Section {idx + 1}" if max_fields > 1 else "Output"
                    embed.add_field(name=field_name, value=chunk, inline=False)
                
                await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.tree.add_command(prompt_command)


MODEL_CHOICES = [
    app_commands.Choice(name="Voxtral Mini", value="voxtral-mini-2507"),
    app_commands.Choice(name="Mistral Small", value="mistral-small-2506"),
    app_commands.Choice(name="GPT 5 Nano (Thinking)", value="gpt-5-nano"),
    app_commands.Choice(name="Voxtral Small", value="voxtral-small-2507"),
    app_commands.Choice(name="GPT OSS (Thinking)", value="openai/gpt-oss-120b"),
    app_commands.Choice(name="Qwen 3 (Thinking)", value="Qwen/Qwen3-235B-A22B-fp8-tput"),
    app_commands.Choice(name="GPT 5 Mini (Thinking)", value="gpt-5-mini"),
    app_commands.Choice(name="Magistral Small (Thinking)", value="magistral-small-2507"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2508"),
    app_commands.Choice(name="DeepSeek R1 (Thinking)", value="deepseek-ai/DeepSeek-R1-0528-tput"),
    app_commands.Choice(name="GPT 5 (Thinking)", value="gpt-5"),
    app_commands.Choice(name="Magistral Medium (Thinking)", value="magistral-medium-2507"),
    app_commands.Choice(name="GPT 4.1", value="gpt-4.1"),
    app_commands.Choice(name="GPT 4.1 Mini", value="gpt-4.1-mini"),
    app_commands.Choice(name="GPT 4.1 Nano", value="gpt-4.1-nano"),
    app_commands.Choice(name="GPT o4 Mini (Thinking)", value="o4-mini"),
]

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="prompt", description="Ask me anything, powered by AI")
@app_commands.describe(
    query="The prompt you want to ask",
    model="Choose the AI model to use",
    image="Upload first image file (for Mistral Small/Medium and GPT-5 models)",
    image2="Upload second image file (for Mistral Small/Medium and GPT-5 models)",
    image3="Upload third image file (for Mistral Small/Medium and GPT-5 models)",
    audio="Upload an audio file (only for Voxtral models)",
)
@app_commands.choices(model=MODEL_CHOICES)
@app_commands.checks.dynamic_cooldown(cooldown)
async def prompt_command(
    interaction: discord.Interaction,
    query: str,
    model: str = "mistral-small-2506",
    image: discord.Attachment = None,
    image2: discord.Attachment = None,
    image3: discord.Attachment = None,
    audio: discord.Attachment = None,
):
    def is_valid_image(attachment: discord.Attachment) -> bool:
        if not attachment:
            return False
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff')
        if attachment.filename.lower().endswith(valid_extensions):
            return True
        if attachment.content_type and attachment.content_type.startswith('image/'):
            return True
        return False

    images = []
    for img in [image, image2, image3]:
        if img:
            images.append(img)

    for img in images:
        if not is_valid_image(img):
            await interaction.response.send_message("Please upload valid image files only.", ephemeral=True)
            return

    if audio and images:
        if audio and (not audio.content_type or not audio.content_type.startswith('audio/')):
            await interaction.response.send_message("Please upload a valid audio file.", ephemeral=True)
            return
        
        conflict_embed = discord.Embed(
            title="⚠️ Media Conflict",
            description="You've uploaded both audio and image files. Please choose which one to use:",
            color=0xff9900
        )
        conflict_embed.add_field(name="Audio File", value=f"🎵 {audio.filename}", inline=True)
        image_names = [img.filename for img in images]
        conflict_embed.add_field(name="Image Files", value=f"🖼️ {', '.join(image_names)}", inline=True)
        
        view = MediaSelectionView(query, model, audio, images, interaction)
        await interaction.response.send_message(embed=conflict_embed, view=view)
        return

    if audio:
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            await interaction.response.send_message("Please upload a valid audio file.", ephemeral=True)
            return
        
        if model not in ["voxtral-mini-2507", "voxtral-small-2507"]:
            model = "voxtral-mini-2507"
    elif images:
        if model not in ["mistral-small-2506", "mistral-medium-2508", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini"]:
            model = "mistral-small-2506"
    else:
        if model in ["voxtral-mini-2507", "voxtral-small-2507"]:
            model = "mistral-small-2506"

    if model == "mistral-small-2506":
        model_name = "Mistral Small"
    elif model == "magistral-small-2507":
        model_name = "Magistral Small"
    elif model == "mistral-medium-2508":
        model_name = "Mistral Medium"
    elif model == "openai/gpt-oss-120b":
        model_name = "GPT OSS"
    elif model == "Qwen/Qwen3-235B-A22B-fp8-tput":
        model_name = "Qwen 3"
    elif model == "magistral-medium-2507":
        model_name = "Magistral Medium"
    elif model == "deepseek-ai/DeepSeek-R1-0528-tput":
        model_name = "DeepSeek R1"
    elif model == "voxtral-mini-2507":
        model_name = "Voxtral Mini"
    elif model == "voxtral-small-2507":
        model_name = "Voxtral Small"
    elif model == "gpt-5-mini":
        model_name = "GPT 5 Mini"
    elif model == "gpt-5-nano":
        model_name = "GPT 5 Nano"
    elif model == "gpt-5":
        model_name = "GPT 5"
    elif model == "gpt-4.1":
        model_name = "GPT 4.1"
    elif model == "gpt-4.1-mini":
        model_name = "GPT 4.1 Mini"
    elif model == "gpt-4.1-nano":
        model_name = "GPT 4.1 Nano"
    elif model == "o4-mini":
        model_name = "GPT o4 Mini"

    thinking_embed = discord.Embed(
        title="🤔 Thinking...",
        description="Processing your prompt with" + f" {model_name}...",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Prompt", value=query[:1000], inline=False)
    if audio:
        thinking_embed.add_field(name="Audio File", value=f"📎 {audio.filename} (using {model_name})", inline=False)
    elif images:
        image_names = [img.filename for img in images]
        thinking_embed.add_field(name="Image Files", value=f"🖼️ {', '.join(image_names)} (using {model_name})", inline=False)

    if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "o4-mini", "gpt-5-nano", "gpt-5-mini", "gpt-5"]:
        view = ThinkingButtonView("Waiting for {} to think... (reclick the button once the output is emitted to see what {} thought.)".format(model_name, model_name))
        await interaction.response.send_message(embed=thinking_embed)
    else:
        await interaction.response.send_message(embed=thinking_embed)

    try:
        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "o4-mini", "gpt-5-nano", "gpt-5-mini", "gpt-5"]:
            answer, think_text = await asyncio.wait_for(
                get_ai_response(query, user_id=interaction.user.id, model=model, 
                              audio_url=audio.url if audio else None,
                              image_urls=[img.url for img in images] if images else None), timeout=360
            )
        else:
            answer = await asyncio.wait_for(
                get_ai_response(query, user_id=interaction.user.id, model=model, 
                              audio_url=audio.url if audio else None,
                              image_urls=[img.url for img in images] if images else None), timeout=60
            )
            think_text = None
    except asyncio.TimeoutError:
        answer = "Sorry, the AI took too long. Try again with a simpler question."
        think_text = None
    except Exception as error:
        answer = f"An error occurred: {error}"
        think_text = None

    response_embed = discord.Embed(title="💡 Output", color=0x34a853)
    response_embed.add_field(name="Prompt", value=query[:1000], inline=False)

    if audio:
        response_embed.add_field(name="Audio File", value=f"[{audio.filename}]({audio.url})", inline=False)
    elif images:
        image_links = [f"[{img.filename}]({img.url})" for img in images]
        response_embed.add_field(name="Image Files", value="\n".join(image_links), inline=False)

    if len(answer) > 1024:
        chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
    else:
        response_embed.add_field(name="Answer", value=answer, inline=False)

    if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507", "magistral-medium-2507", "openai/gpt-oss-120b", "o4-mini", "gpt-5-nano", "gpt-5-mini", "gpt-5"] and think_text:
        view = ThinkingButtonView(think_text or "No thinking output available.")
        await interaction.edit_original_response(embed=response_embed, view=view)
    else:
        await interaction.edit_original_response(embed=response_embed)
