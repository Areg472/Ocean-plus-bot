import discord
from discord import app_commands
import random
from commands.utils import cooldown

def setup(bot):
    """
    Register the got_a_life command with the bot
    """
    bot.tree.add_command(got_a_life_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="got_a_life", description="Check if you have a life or not")
@app_commands.checks.dynamic_cooldown(cooldown)
async def got_a_life_command(interaction: discord.Interaction):
    life_check = random.choices([0, 1], weights=[75, 25], k=1)[0]
    message = "You have a life!" if life_check == 1 else "You don't have a life!"
    await interaction.response.send_message(message)