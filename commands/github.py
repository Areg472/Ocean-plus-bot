import discord
from discord import app_commands
import requests
from commands.utils import cooldown

def setup(bot):bot.tree.add_command(github_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="github", description="Get github info of a user")
@app_commands.describe(username="The username you want to get github info of")
@app_commands.checks.dynamic_cooldown(cooldown)
async def github_command(interaction: discord.Interaction, username: str):
    response = requests.get(f"https://api.popcat.xyz/v2/github/{username}")
    json_data = response.json()
    github_name = json_data['message']['name']
    github_url = json_data['message']['url']
    github_avatar = json_data['message']['avatar']
    github_location = json_data['message']['location']
    github_bio = json_data['message']['bio']
    result = discord.Embed(title=f"Github info of {github_name}!", colour=discord.Colour.dark_blue()).add_field(
        name="Name", value=github_name, inline=False).add_field(
        name="Location", value=github_location, inline=False).add_field(
        name="Bio", value=github_bio, inline=False).add_field(
        name="Github URL", value=github_url, inline=False).set_thumbnail(
        url=github_avatar)
    await interaction.response.send_message(embed=result)