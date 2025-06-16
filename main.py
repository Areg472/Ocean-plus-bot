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
                await message.channel.send("https://tenor.com/view/tim-hortons-its-time-for-tims-tims-timmies-canadian-fast-food-gif-2625977777736951761")
                time.sleep(0.5)
                await message.channel.send("https://tenor.com/view/aclogo-accessibility-club-leland-lhs-accessibilty-accessibility-gif-18778419")
                time.sleep(0.5)
                await message.channel.send("https://tenor.com/view/ok-okay-like-emoticon-emoji-gif-8063975731664111")
                time.sleep(0.5)
                await message.channel.send("https://tenor.com/view/taco-bell-tex-mex-tacos-fast-food-gif-10761685082235406599")
                time.sleep(0.5)
                await message.channel.send("https://tenor.com/view/aclogo-accessibility-club-leland-lhs-accessibilty-accessibility-gif-18778419")
                time.sleep(0.5)
                await message.channel.send("https://tenor.com/view/no-dislike-thumbs-down-emoticon-emoji-gif-6511007033097383174")
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
