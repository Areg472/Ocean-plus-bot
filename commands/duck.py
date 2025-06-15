import discord
from discord import app_commands
import requests
import random
from commands.utils import cooldown

def setup(bot):
    """
    Register the duck command with the bot
    """
    bot.tree.add_command(duck_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="duck", description="Get an UwU duck picture")
@app_commands.checks.dynamic_cooldown(cooldown)
async def duck_command(interaction: discord.Interaction):
    response = requests.get("https://random-d.uk/api/random")
    json_data = response.json()
    hmmmmmm = random.randint(1, 20)
    if hmmmmmm == 1:
        await interaction.response.send_message("<:duck:1313390002805411872>")
    else:
        await interaction.response.send_message(json_data['url'])