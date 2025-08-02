import discord
from discord import app_commands
import requests
from commands.utils import cooldown

def setup(bot):bot.tree.add_command(joke_overhead_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="joke_overhead", description="Use this and mention the guy that doesn't understand jokes!")
@app_commands.describe(the_guy="The guy that doesn't understand jokes")
@app_commands.checks.dynamic_cooldown(cooldown)
async def joke_overhead_command(interaction: discord.Interaction, the_guy: discord.User):
    avatar_url = the_guy.avatar.url + ".png"
    response = requests.get(f"https://api.popcat.xyz/v2/jokeoverhead?image={avatar_url}")
    await interaction.response.send_message(response.url)