import discord
import os
import logging
import aiohttp
import random
from discord.app_commands import CommandOnCooldown
from discord import app_commands
from discord.ext import commands
from commands import setup_commands

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

tracked_messages = {}

boardgames_enabled = False
boardgame_names = [
    "Azul", "Ticket To Ride", "Catan", "Scout!", "Heat Pedal To The Metal", "Lost Cities", "Wingspan", "Brass Birmingham", "Gloomhaven", 
    "Pandemic", "Carcassonne", "7 Wonders", "Terraforming Mars", "Patchwork", "Codenames", "Dominion"
]

@bot.event
async def on_ready():
    setup_commands(bot)

    await bot.tree.sync()

    print(f'Logged in as {bot.user}!')


@bot.event
async def on_message(message: discord.Message):

    if message.guild and message.guild.id == 1335634554169327646:
        if message.content.strip().lower() == "!boardgames":
            global boardgames_enabled
            boardgames_enabled = not boardgames_enabled
            status = "enabled" if boardgames_enabled else "disabled"
            await message.channel.send(f"Boardgames feature is now {status}.")
            return

        if boardgames_enabled:
            lowered = message.content.lower()
            if "monopoly" in lowered or "uno" in lowered:
                await message.delete()
                chosen = random.choice(boardgame_names)
                await message.channel.send(f"{message.author.mention} loves {chosen}")
                return

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, CommandOnCooldown):
        seconds = round(error.retry_after + 0.5)
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {seconds} seconds.",
            ephemeral=True
        )



bot.run(os.environ.get('TOKEN'))
