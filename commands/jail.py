import discord
from discord import app_commands
import requests
from commands.utils import cooldown

def setup(bot):
    """
    Register the jail command with the bot
    """
    bot.tree.add_command(jail_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="jail", description="Put the mentioned user in jail!")
@app_commands.describe(person="The person you want to go to jail!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def jail_command(interaction: discord.Interaction, person: discord.User):
    avatar_url = person.avatar.url
    response = requests.get(f"https://api.popcat.xyz/v2/jail?image={avatar_url}")
    await interaction.response.send_message(response.url)