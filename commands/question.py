import discord
from discord import app_commands
from commands.utils import cooldown, get_gemini_response
import asyncio

def setup(bot):
    """
    Register the question command with the bot
    """
    bot.tree.add_command(question_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="question", description="Ask me anything, powered by Gemini")
@app_commands.describe(query="What's the question? Be concise!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def question_command(interaction: discord.Interaction, query: str):
    # Create thinking embed
    thinking_embed = discord.Embed(
        title="🤔 Thinking...",
        description="Processing your question with Gemini AI...",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Question", value=query[:1000] + ("..." if len(query) > 1000 else ""), inline=False)
    
    await interaction.response.send_message(embed=thinking_embed)

    try:
        # Add timeout wrapper
        answer = await asyncio.wait_for(get_gemini_response(query, user_id=interaction.user.id), timeout=60.0)
    except asyncio.TimeoutError:
        answer = "Sorry, the AI took too long to respond. Please try again with a simpler question."
    except Exception as e:
        print(f"Unexpected error in question command: {e}")
        answer = "Sorry, something went wrong while processing your question."
    
    # Ensure we always have some response
    if not answer:
        answer = "Sorry, I couldn't generate a response. Please try again."
    
    # Create response embed
    response_embed = discord.Embed(
        title="💡 Answer",
        color=0x34a853
    )
    response_embed.add_field(name="Question", value=query[:1000] + ("..." if len(query) > 1000 else ""), inline=False)
    
    # Handle long responses
    if len(answer) > 1900:  # Leave room for embed formatting
        chunks = [answer[i:i + 1900] for i in range(0, len(answer), 1900)]
        response_embed.add_field(name="Answer (Part 1)", value=chunks[0], inline=False)
        await interaction.edit_original_response(embed=response_embed)
        
        # Send additional parts as follow-up embeds
        for i, chunk in enumerate(chunks[1:], 2):
            continuation_embed = discord.Embed(
                title=f"💡 Answer (Part {i})",
                description=chunk,
                color=0x34a853
            )
            await interaction.followup.send(embed=continuation_embed)
    else:
        response_embed.add_field(name="Answer", value=answer, inline=False)
        await interaction.edit_original_response(embed=response_embed)