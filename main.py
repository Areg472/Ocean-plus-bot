import random
import time

import discord
import os
import logging
from discord.app_commands import CommandOnCooldown
from discord import app_commands
from discord.ext import commands
from commands import setup_commands
from commands.utils import get_gemini_response, user_history, MAX_HISTORY

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    setup_commands(bot)

    await bot.tree.sync()

    print(f'Logged in as {bot.user}!')
    channel = bot.get_channel(1335634555377291306)
    await channel.send("Tim hortons is the best!")


@bot.event
async def on_message(message: discord.Message):
    from commands.generate_code import user_codes
    
    if message.author.bot:
        return

    if message.guild and message.guild.id == 1335634554169327646:
        user_id = message.author.id
        message_content = message.content.strip()
        
        if user_id in user_codes and user_codes[user_id]["code"] == message_content:
            context = user_codes[user_id]["context"]
            if context == 1:
                await message.delete()
                await message.channel.send(
                    "<@1299815086147502080> https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB"
                )
                await message.channel.send(
                    "https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcP1o5iDc2RNu8TqO3d9QrgzXCYhmV2IlEJUSZ0"
                )
            elif context == 2:
                await message.delete()
                await message.channel.send("https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPm20fUWgarYbdC3iT9GeS4kf6UyAKLjp7uFNM")
                time.sleep(1)
                await message.channel.send("https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPQ24mpNuvmSEAv0yirJneg9hcBMoC3TQuRt2s")
                time.sleep(1)
                await message.channel.send("https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPQgtI2BvmSEAv0yirJneg9hcBMoC3TQuRt2sH")
                time.sleep(1)
                await message.channel.send("https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPeES8RvnilWqd9IHpjOJDSQ5tT1Xg2Vr0ZF4B")
                time.sleep(1)
                await message.channel.send("https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPQ24mpNuvmSEAv0yirJneg9hcBMoC3TQuRt2s")
                time.sleep(1)
                await message.channel.send("https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPfA1ADBlBVdGovX205z9aWg8ep4Nb6xqLZIEr")
            del user_codes[user_id]
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
