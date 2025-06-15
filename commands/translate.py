import discord
from discord import app_commands
import requests
from typing import Optional
from commands.utils import cooldown

def get_translation(text, target_language):
    """
    Translate text to the specified language
    """
    response = requests.get(f'https://api.popcat.xyz/v2/translate?to={target_language}&text={text}')
    if response.status_code == 200:
        json_data = response.json()
        return json_data['translated']
    else:
        return "Could not fetch the translation at this time."

def setup(bot):
    """
    Register the translate command with the bot
    """
    bot.tree.add_command(translate_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="translate", description="Translate text to a specified language")
@app_commands.describe(text="The text to translate", target_language="The target language.")
@app_commands.checks.dynamic_cooldown(cooldown)
async def translate_command(interaction: discord.Interaction, text: str, target_language: Optional[str] = "en"):
    translation = get_translation(text, target_language)
    await interaction.response.send_message(translation)