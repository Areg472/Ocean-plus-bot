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
            model = "mistral-small-2506" if self.model not in ["mistral-small-2506", "mistral-medium-2505"] else self.model
            model_name = "Mistral Small" if model == "mistral-small-2506" else "Mistral Medium"
            image_names = [img.filename for img in self.images]
            media_description = f"🖼️ {', '.join(image_names)}"

        thinking_embed = discord.Embed(
            title="🤔 Thinking...",
            description=f"Processing your prompt with {model_name}...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="Prompt", value=self.query[:1000], inline=False)
        thinking_embed.add_field(name="Media Files", value=f"{media_description} (using {model_name})", inline=False)

        await interaction.edit_original_response(embed=thinking_embed, view=None)

        try:
            if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507"]:
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

        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507"]:
            view = ThinkingButtonView(think_text or "No <think> output found.")
            await interaction.edit_original_response(embed=response_embed, view=view)
        else:
            await interaction.edit_original_response(embed=response_embed)

class ThinkingButtonView(discord.ui.View):
    def __init__(self, thinking_text: str):
        super().__init__(timeout=180)
        self.thinking_text = thinking_text

    @discord.ui.button(label="Show Thinking Output", style=discord.ButtonStyle.secondary)
    async def show_thinking(self, interaction: discord.Interaction, button: discord.ui.Button):
        chunks = [self.thinking_text[i:i+1024] for i in range(0, len(self.thinking_text), 1024)]
        embed = discord.Embed(title="Thinking Output", color=0x4285f4)
        for idx, chunk in enumerate(chunks, start=1):
            embed.add_field(name=f"Output Part {idx}", value=chunk, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.tree.add_command(prompt_command)


MODEL_CHOICES = [
    app_commands.Choice(name="Voxtral Mini", value="voxtral-mini-2507"),
    app_commands.Choice(name="Mistral Small", value="mistral-small-2506"),
    app_commands.Choice(name="Devstral Small", value="devstral-small-2507"),
    app_commands.Choice(name="Voxtral Small", value="voxtral-small-2507"),
    app_commands.Choice(name="GPT OSS", value="openai/gpt-oss-120b"),
    app_commands.Choice(name="Qwen 3 (Thinking)", value="Qwen/Qwen3-235B-A22B-fp8-tput"),
    app_commands.Choice(name="Magistral Small (Thinking)", value="magistral-small-2507"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2505"),
    app_commands.Choice(name="DeepSeek R1 (Thinking)", value="deepseek-ai/DeepSeek-R1-0528-tput"),
]

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="prompt", description="Ask me anything, powered by AI")
@app_commands.describe(
    query="The prompt you want to ask",
    model="Choose the AI model to use",
    image="Upload first image file (only for Mistral Small/Medium)",
    image2="Upload second image file (only for Mistral Small/Medium)",
    image3="Upload third image file (only for Mistral Small/Medium)",
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
        if model not in ["mistral-small-2506", "mistral-medium-2505"]:
            model = "mistral-small-2506"
    else:
        if model in ["voxtral-mini-2507", "voxtral-small-2507"]:
            model = "mistral-small-2506"

    if model == "devstral-small-2507":
        model_name = "Devstral Small"
    elif model == "mistral-small-2506":
        model_name = "Mistral Small"
    elif model == "magistral-small-2507":
        model_name = "Magistral Small"
    elif model == "mistral-medium-2505":
        model_name = "Mistral Medium"
    elif model == "openai/gpt-oss-120b":
        model_name = "GPT OSS"
    elif model == "Qwen/Qwen3-235B-A22B-fp8-tput":
        model_name = "Qwen 3"
    elif model == "deepseek-ai/DeepSeek-R1-0528-tput":
        model_name = "DeepSeek R1"
    elif model == "voxtral-mini-2507":
        model_name = "Voxtral Mini"
    elif model == "voxtral-small-2507":
        model_name = "Voxtral Small"

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

    if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput"]:
        view = ThinkingButtonView(f"Waiting for {model_name} to think...(reclick the button once the output is emitted to see what {model_name} thought.)")
        await interaction.response.send_message(embed=thinking_embed, view=view)
    else:
        await interaction.response.send_message(embed=thinking_embed)

    try:
        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507"]:
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

    if model == "devstral-small-2507":
        response_embed = discord.Embed(title="💡 Answer", color=0x34a853)
        response_embed.add_field(name="Question", value=query[:1000], inline=False)

        code_block_pattern = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)
        parts = []
        last_end = 0
        for match in code_block_pattern.finditer(answer):
            if match.start() > last_end:
                before = answer[last_end:match.start()]
                for i in range(0, len(before), 1024):
                    chunk = before[i:i+1024]
                    if chunk.strip():
                        parts.append(("text", chunk))
            code_block = match.group(1)
            parts.append(("code", code_block))
            last_end = match.end()
        if last_end < len(answer):
            after = answer[last_end:]
            for i in range(0, len(after), 1024):
                chunk = after[i:i+1024]
                if chunk.strip():
                    parts.append(("text", chunk))

        field_idx = 1
        followup_codeblocks = []
        for typ, chunk in parts:
            if typ == "code" and len(chunk) > 1024:
                followup_codeblocks.append(chunk)
            else:
                response_embed.add_field(name=f"Answer (Part {field_idx})", value=chunk, inline=False)
                field_idx += 1

        try:
            await interaction.edit_original_response(embed=response_embed)
            for codeblock in followup_codeblocks:
                await interaction.followup.send(codeblock)
        except Exception as e:
            await interaction.followup.send(embed=response_embed)
            for codeblock in followup_codeblocks:
                await interaction.followup.send(codeblock)
    else:
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

        if model in ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "magistral-small-2507"]:
            view = ThinkingButtonView(think_text or "No <think> output found.")
            await interaction.edit_original_response(embed=response_embed, view=view)
        else:
            await interaction.edit_original_response(embed=response_embed)