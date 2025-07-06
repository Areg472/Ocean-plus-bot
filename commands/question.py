import discord
from discord import app_commands
from commands.utils import cooldown, get_mistral_response
import asyncio
import re


MODEL_CHOICES = [
    app_commands.Choice(name="Mistral Small", value="mistral-small-2506"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2505"),
    app_commands.Choice(name="Codestral", value="codestral-2501"),
]


def setup(bot):
    """
    Register the question command with the bot.
    """
    bot.tree.add_command(question_command)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="question", description="Ask me anything, powered by Mistral")
@app_commands.describe(
    query="The question or prompt you want to ask",
    model="Choose the Mistral model to use"
)
@app_commands.choices(model=MODEL_CHOICES)
@app_commands.checks.dynamic_cooldown(cooldown)
async def question_command(
    interaction: discord.Interaction,
    query: str,
    model: str = "mistral-small-2506"  # Default to Mistral Small
):
    # If Codestral is selected, use plain text messages
    if model == "codestral-2501":
        # Thinking embed for Codestral
        thinking_embed = discord.Embed(
            title="🤔 Thinking...",
            description="Processing your question with Codestral...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="Question", value=query[:1000], inline=False)
        await interaction.response.send_message(embed=thinking_embed)
    else:
        # Thinking embed
        thinking_embed = discord.Embed(
            title="🤔 Thinking...",
            description="Processing your question with Mistral AI...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="Question", value=query[:1000], inline=False)
        await interaction.response.send_message(embed=thinking_embed)

    # Mistral call
    try:
        # Get the streamed response
        answer = await asyncio.wait_for(
            get_mistral_response(query, user_id=interaction.user.id, model=model), timeout=60.0
        )
    except asyncio.TimeoutError:
        answer = "Sorry, the AI took too long. Try again with a simpler question."
    except Exception as error:
        answer = f"An error occurred: {error}"

    if model == "codestral-2501":
        # Prepare embed response for Codestral
        response_embed = discord.Embed(title="💡 Answer", color=0x34a853)
        response_embed.add_field(name="Question", value=query[:1000], inline=False)

        # Split the answer into chunks of 1024 characters, but keep code blocks together
        code_block_pattern = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)
        parts = []
        last_end = 0
        for match in code_block_pattern.finditer(answer):
            # Add text before code block
            if match.start() > last_end:
                before = answer[last_end:match.start()]
                # Split before into 1024 chunks
                for i in range(0, len(before), 1024):
                    chunk = before[i:i+1024]
                    if chunk.strip():
                        parts.append(chunk)
            # Add the code block as a whole
            code_block = match.group(1)
            parts.append(code_block)
            last_end = match.end()
        # Add any remaining text after the last code block
        if last_end < len(answer):
            after = answer[last_end:]
            for i in range(0, len(after), 1024):
                chunk = after[i:i+1024]
                if chunk.strip():
                    parts.append(chunk)

        # Now add each part as a field
        for idx, chunk in enumerate(parts, start=1):
            response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)

        try:
            await interaction.edit_original_response(embed=response_embed)
        except Exception as e:
            # fallback: send as followup if editing fails
            await interaction.followup.send(embed=response_embed)
    else:
        # Prepare embed response
        response_embed = discord.Embed(title="💡 Answer", color=0x34a853)
        response_embed.add_field(name="Question", value=query[:1000], inline=False)

        # Split the answer into chunks of 1024 characters
        if len(answer) > 1024:
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
        else:
            response_embed.add_field(name="Answer", value=answer, inline=False)

        # Send the response embed
        await interaction.edit_original_response(embed=response_embed)