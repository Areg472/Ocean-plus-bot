import discord
from discord import app_commands
from commands.utils import cooldown, get_ai_response
import asyncio
import re


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
    app_commands.Choice(name="Mistral Small", value="mistral-small-2506"),
    app_commands.Choice(name="Devstral Small", value="devstral-small-2507"),
    app_commands.Choice(name="Qwen 3 235B", value="Qwen/Qwen3-235B-A22B-Instruct-2507-tput"),
    app_commands.Choice(name="Magistral Small", value="magistral-small-2506"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2505"),
    app_commands.Choice(name="DeepSeek R1", value="deepseek-ai/DeepSeek-R1-0528-tput"),
]

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="prompt", description="Ask me anything, powered by AI")
@app_commands.describe(
    query="The prompt you want to ask",
    model="Choose the AI model to use"
)
@app_commands.choices(model=MODEL_CHOICES)
@app_commands.checks.dynamic_cooldown(cooldown)
async def prompt_command(
    interaction: discord.Interaction,
    query: str,
    model: str = "mistral-small-2506"  # Default to Mistral Small
):
    if model == "devstral-small-2507":
        model_name = "Devstral Small"
    elif model == "mistral-small-2506":
        model_name = "Mistral Small"
    elif model == "magistral-small-2506":
        model_name = "Magistral Small"
    elif model == "mistral-medium-2505":
        model_name = "Mistral Medium"
    elif model == "Qwen/Qwen3-235B-A22B-Instruct-2507-tput":
        model_name = "Qwen 3"
    elif model == "deepseek-ai/DeepSeek-R1-0528-tput":
        model_name = "DeepSeek R1"

    thinking_embed = discord.Embed(
        title="🤔 Thinking...",
        description="Processing your question with" + f" {model_name}...",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Question", value=query[:1000], inline=False)

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
                get_ai_response(query, user_id=interaction.user.id, model=model), timeout=360
            )
        else:
            answer = await asyncio.wait_for(
                get_ai_response(query, user_id=interaction.user.id, model=model), timeout=60
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
        response_embed = discord.Embed(title="💡 Answer", color=0x34a853)
        response_embed.add_field(name="Question", value=query[:1000], inline=False)

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