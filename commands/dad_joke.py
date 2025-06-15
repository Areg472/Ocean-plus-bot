import discord
from discord import app_commands
import requests
import random
from commands.utils import cooldown

def setup(bot):
    """
    Register the dad_joke command with the bot
    """
    bot.tree.add_command(dad_joke_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="dad_joke", description="Generates a random dad joke!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def dad_joke_command(interaction: discord.Interaction):
    response = requests.get("https://api.popcat.xyz/v2/joke")
    json_data = response.json()
    nothing = random.randint(1, 20)
    if nothing == 1:
        await interaction.response.send_message('"Why does Areg break this bot a lot? Because he is broken."')
    else:
        await interaction.response.send_message(f"\"{json_data['message']['joke']}\"")