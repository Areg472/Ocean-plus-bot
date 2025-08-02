import discord
from discord import app_commands
import requests
from commands.utils import cooldown

def setup(bot):bot.tree.add_command(mock_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="mock", description="Make your message wEirD aS hEll")
@app_commands.describe(message="The message to mock")
@app_commands.checks.dynamic_cooldown(cooldown)
async def mock_command(interaction: discord.Interaction, message: str):
    response = requests.get("https://api.popcat.xyz/v2/mock?text=" + message)
    json_data = response.json()
    await interaction.response.send_message(json_data['message']['text'])