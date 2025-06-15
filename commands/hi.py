import discord
from discord import app_commands
from commands.utils import cooldown

def setup(bot):
    """
    Register the hi command with the bot
    """
    bot.tree.add_command(hi_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="hi", description="Say hi to the bot!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def hi_command(interaction: discord.Interaction):
    await interaction.response.send_message('Hi. I am the official Ocean+ discord bot!')