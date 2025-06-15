import discord
from discord import app_commands
import requests
from commands.utils import cooldown

def setup(bot):
    """
    Register the text_to_morse command with the bot
    """
    bot.tree.add_command(text_to_morse_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="text_to_morse", description="Translate text to morse")
@app_commands.describe(text="The text to translate")
@app_commands.checks.dynamic_cooldown(cooldown)
async def text_to_morse_command(interaction: discord.Interaction, text: str):
    response = requests.get(f"https://api.popcat.xyz/v2/texttomorse?text={text}")
    json_data = response.json()
    morse_text = json_data['message']['morse']
    morse_embed = discord.Embed(title="Text to Morse", colour=discord.Colour.dark_blue()).add_field(
        name="Original", value=text, inline=False).add_field(
        name="Morse", value=morse_text, inline=False)
    await interaction.response.send_message(embed=morse_embed)