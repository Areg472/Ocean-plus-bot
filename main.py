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

# Boardgames feature toggle
boardgames_enabled = True
boardgame_names = [
    "Azul", "Ticket To Ride", "Catan", "Scout!", "Head Pedal To The Metal", "Lost Cities"
]

@bot.event
async def on_ready():
    setup_commands(bot)

    await bot.tree.sync()

    print(f'Logged in as {bot.user}!')


@bot.event
async def on_message(message: discord.Message):
    """
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
                msg1 = await message.channel.send(
                    "<@1299815086147502080> https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB"
                )
                msg2 = await message.channel.send(
                    "https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcP1o5iDc2RNu8TqO3d9QrgzXCYhmV2IlEJUSZ0"
                )

                current_time = time.time()
                tracked_messages[msg1.id] = {
                    "content": "https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB",
                    "channel": message.channel,
                    "timestamp": current_time
                }
                tracked_messages[msg2.id] = {
                    "content": "https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcP1o5iDc2RNu8TqO3d9QrgzXCYhmV2IlEJUSZ0",
                    "channel": message.channel,
                    "timestamp": current_time
                }

                asyncio.create_task(cleanup_tracked_message(msg1.id, current_time))
                asyncio.create_task(cleanup_tracked_message(msg2.id, current_time))

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
    """

    # Only process messages in the target server
    if message.guild and message.guild.id == 1335634554169327646:
        # Toggle command
        if message.content.strip().lower() == "!boardgames":
            global boardgames_enabled
            boardgames_enabled = not boardgames_enabled
            status = "enabled" if boardgames_enabled else "disabled"
            await message.channel.send(f"Boardgames feature is now {status}.")
            return

        # Check for monopoly or uno
        if boardgames_enabled:
            lowered = message.content.lower()
            if "monopoly" in lowered or "uno" in lowered:
                chosen = random.choice(boardgame_names)
                await message.channel.send(f"{message.author.mention} likes {chosen}")
                return

    """
@bot.event
async def on_message_delete(message: discord.Message):
    if message.id in tracked_messages:
        tracked_msg = tracked_messages[message.id]
        current_time = time.time()

        if current_time - tracked_msg["timestamp"] <= 120:
            try:
                new_msg = await tracked_msg["channel"].send(tracked_msg["content"])

                tracked_messages[new_msg.id] = {
                    "content": tracked_msg["content"],
                    "channel": tracked_msg["channel"],
                    "timestamp": tracked_msg["timestamp"]
                }
            except discord.errors.Forbidden:
                pass

        del tracked_messages[message.id]

async def cleanup_tracked_message(message_id: int, timestamp: float):
    await asyncio.sleep(120)
    if message_id in tracked_messages and tracked_messages[message_id]["timestamp"] == timestamp:
        del tracked_messages[message_id]
"""
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, CommandOnCooldown):
        seconds = round(error.retry_after + 0.5)
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {seconds} seconds.",
            ephemeral=True
        )



bot.run(os.environ.get('TOKEN'))
