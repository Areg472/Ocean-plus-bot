import discord
from discord import app_commands
import requests
import json
import random
from commands.utils import cooldown

def get_meme():
    while True:
        response = requests.get('https://meme-api.com/gimme')
        json_data = json.loads(response.text)
        if not json_data.get('nsfw', True):
            return json_data['url']

def setup(bot):
    bot.tree.add_command(meme_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="meme", description="Send a funny meme!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def meme_command(interaction: discord.Interaction):
    meme_url = get_meme()
    wtf = random.randint(1, 19)
    if wtf == 1:
        await interaction.response.send_message("Errm What the Sigma?")
    elif wtf == 2:
        await interaction.response.send_message("Skibidi toilet sigma aura rizz fanum tax - no one")
    else:
        await interaction.response.send_message(meme_url)