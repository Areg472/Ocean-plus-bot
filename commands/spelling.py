import discord
from discord import app_commands
import language_tool_python

tool = language_tool_python.LanguageToolPublicAPI('en-US')

def setup(bot):
    bot.tree.add_command(spelling_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name="Spelling Checker")
async def spelling_command(interaction: discord.Interaction, message: discord.Message):
    text = str(message.content)
    suggest = tool.correct(text)
    await interaction.response.send_message(f'Errm did you mean "{suggest}"?')