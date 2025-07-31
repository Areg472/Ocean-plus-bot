import discord
from discord import app_commands
from commands.utils import cooldown, get_ai_response
import asyncio
import re


class MediaSelectionView(discord.ui.View):
    def __init__(self, query: str, model: str, audio: discord.Attachment, image: discord.Attachment, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.query = query
        self.model = model
        self.audio = audio
        self.image = image
        self.original_interaction = interaction

    @discord.ui.button(label="Use Audio", style=discord.ButtonStyle.secondary, emoji="🎵")
    async def use_audio(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.process_prompt(interaction, use_audio=True)

    @discord.ui.button(label="Use Image", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def use_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.process_prompt(interaction, use_audio=False)

    async def process_prompt(self, interaction: discord.Interaction, use_audio: bool):
        if use_audio:
            model = "voxtral-mini-2507" if self.model not in ["voxtral-mini-2507", "voxtral-small-2507"] else self.model
            model_name = "Voxtral Mini" if model == "voxtral-mini-2507" else "Voxtral Small"
            media_file = self.audio
        else:
            model = "mistral-small-2506" if self.model not in ["mistral-small-2506", "mistral-medium-2505"] else self.model
            model_name = "Mistral Small" if model == "mistral-small-2506" else "Mistral Medium"
            media_file = self.image

        thinking_embed = discord.Embed(
            title="🤔 Thinking...",
            description=f"Processing your prompt with {model_name}...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="Prompt", value=self.query[:1000], inline=False)
        thinking_embed.add_field(name="Media File", value=f"📎 {media_file.filename} (using {model_name})", inline=False)

        await interaction.edit_original_response(embed=thinking_embed, view=None)

        try:
            if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                answer, think_text = await asyncio.wait_for(
                    get_ai_response(self.query, user_id=self.original_interaction.user.id, model=model, 
                                  audio_url=self.audio.url if use_audio else None,
                                  image_url=self.image.url if not use_audio else None), timeout=360
                )
            else:
                answer = await asyncio.wait_for(
                    get_ai_response(self.query, user_id=self.original_interaction.user.id, model=model,
                                  audio_url=self.audio.url if use_audio else None,
                                  image_url=self.image.url if not use_audio else None), timeout=60
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
        response_embed.add_field(name="Media File", value=f"[{media_file.filename}]({media_file.url})", inline=False)

        if len(answer) > 1024:
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
        else:
            response_embed.add_field(name="Answer", value=answer, inline=False)

        if model == "deepseek-ai/DeepSeek-R1-0528-tput":
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
    app_commands.Choice(name="Qwen 3 235B", value="Qwen/Qwen3-235B-A22B-Instruct-2507-tput"),
    app_commands.Choice(name="Magistral Small", value="magistral-small-2507"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2505"),
    app_commands.Choice(name="DeepSeek R1", value="deepseek-ai/DeepSeek-R1-0528-tput"),
]

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="prompt", description="Ask me anything, powered by AI")
@app_commands.describe(
    query="The prompt you want to ask",
    model="Choose the AI model to use",
    image="Upload an image file (only for Mistral Small/Medium)",
    audio="Upload an audio file (only for Voxtral models)",
)
@app_commands.choices(model=MODEL_CHOICES)
@app_commands.checks.dynamic_cooldown(cooldown)
async def prompt_command(
    interaction: discord.Interaction,
    query: str,
    model: str = "mistral-small-2506",  # Default to Mistral Small
    audio: discord.Attachment = None,
    image: discord.Attachment = None
):
    # Handle conflicts when both audio and image are provided
    if audio and image:
        # Check if files are valid
        if audio and (not audio.content_type or not audio.content_type.startswith('audio/')):
            await interaction.response.send_message("Please upload a valid audio file.", ephemeral=True)
            return
        if image and (not image.content_type or not image.content_type.startswith('image/')):
            await interaction.response.send_message("Please upload a valid image file.", ephemeral=True)
            return
        
        conflict_embed = discord.Embed(
            title="⚠️ Media Conflict",
            description="You've uploaded both audio and image files. Please choose which one to use:",
            color=0xff9900
        )
        conflict_embed.add_field(name="Audio File", value=f"🎵 {audio.filename}", inline=True)
        conflict_embed.add_field(name="Image File", value=f"🖼️ {image.filename}", inline=True)
        
        view = MediaSelectionView(query, model, audio, image, interaction)
        await interaction.response.send_message(embed=conflict_embed, view=view)
        return

    # Handle model switching based on media presence
    if audio:
        # Check if it's an audio file
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            await interaction.response.send_message("Please upload a valid audio file.", ephemeral=True)
            return
        
        # Switch to Voxtral Mini if not already a Voxtral model
        if model not in ["voxtral-mini-2507", "voxtral-small-2507"]:
            model = "voxtral-mini-2507"
    elif image:
        # Check if it's an image file
        if not image.content_type or not image.content_type.startswith('image/'):
            await interaction.response.send_message("Please upload a valid image file.", ephemeral=True)
            return
        
        # Switch to Mistral Small if not already a compatible model
        if model not in ["mistral-small-2506", "mistral-medium-2505"]:
            model = "mistral-small-2506"
    else:
        # Switch to Mistral Small if Voxtral model selected but no audio
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
    elif model == "Qwen/Qwen3-235B-A22B-Instruct-2507-tput":
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
    elif image:
        thinking_embed.add_field(name="Image File", value=f"🖼️ {image.filename} (using {model_name})", inline=False)

    # For DeepSeek R1, show button but don't set thinking_output yet
    if model == "deepseek-ai/DeepSeek-R1-0528-tput":
        # Attach the view with a placeholder text
        view = ThinkingButtonView("Waiting for DeepSeek to think...(reclick the button once the output is emitted to see what DeepSeek thought.)")
        await interaction.response.send_message(embed=thinking_embed, view=view)
    else:
        await interaction.response.send_message(embed=thinking_embed)

    try:
        if model == "deepseek-ai/DeepSeek-R1-0528-tput":
            answer, think_text = await asyncio.wait_for(
                get_ai_response(query, user_id=interaction.user.id, model=model, 
                              audio_url=audio.url if audio else None,
                              image_url=image.url if image else None), timeout=360
            )
        else:
            answer = await asyncio.wait_for(
                get_ai_response(query, user_id=interaction.user.id, model=model, 
                              audio_url=audio.url if audio else None,
                              image_url=image.url if image else None), timeout=60
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
        
        # Add media file link
        if audio:
            response_embed.add_field(name="Audio File", value=f"[{audio.filename}]({audio.url})", inline=False)
        elif image:
            response_embed.add_field(name="Image File", value=f"[{image.filename}]({image.url})", inline=False)

        if len(answer) > 1024:
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
        else:
            response_embed.add_field(name="Answer", value=answer, inline=False)

        # For DeepSeek R1, edit with the view and set the real think_text
        if model == "deepseek-ai/DeepSeek-R1-0528-tput":
            # Update the view with the real think_text
            view = ThinkingButtonView(think_text or "No <think> output found.")
            await interaction.edit_original_response(embed=response_embed, view=view)
        else:
            await interaction.edit_original_response(embed=response_embed)