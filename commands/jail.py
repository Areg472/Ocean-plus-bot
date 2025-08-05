import discord
from discord import app_commands
import requests
from commands.utils import cooldown
import urllib.parse

def setup(bot):bot.tree.add_command(jail_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="jail", description="Put the mentioned user in jail!")
@app_commands.describe(person="The person you want to go to jail!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def jail_command(interaction: discord.Interaction, person: discord.User):
    if person.avatar:
        avatar_url = person.avatar.url
    else:
        avatar_url = person.default_avatar.url
    encoded_url = urllib.parse.quote(avatar_url, safe='')
    api_url = f"https://api.popcat.xyz/v2/jail?image={encoded_url}"
    response = requests.get(api_url)
    await interaction.response.send_message(response.url)