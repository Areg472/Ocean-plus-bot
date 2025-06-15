import discord
from discord import app_commands
from commands.utils import cooldown, get_gemini_response

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
    await interaction.response.defer()

    answer = await get_gemini_response(query)
    if answer:
        if len(answer) > 2000:
            chunks = [answer[i:i + 1900] for i in range(0, len(answer), 1900)]
            for chunk in chunks:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(answer)
    else:
        await interaction.followup.send("Sorry, I couldn't generate a response at this time.")