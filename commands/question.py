import discord
from discord import app_commands
from commands.utils import cooldown, get_mistral_response
import asyncio


MODEL_CHOICES = [
    app_commands.Choice(name="Mistral Small", value="mistral-small-2506"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2505"),
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