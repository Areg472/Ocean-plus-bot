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

    # Check for user codes in the specific channel 1335634555377291306
    if message.channel.id == 1183318047717601312:
        user_id = message.author.id
        message_content = message.content.strip()
        
        # Check if the message matches any user's code
        if user_id in user_codes and user_codes[user_id] == message_content:
            # Send the Ocean+ link
            await message.channel.send(
                "<@1299815086147502080> https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB"            )
            # Reset the code for this user
            del user_codes[user_id]
        return  # Always return after processing messages in this channel

    # Handle AI chat channel
    if message.channel.id != 1315586087573258310:
        return

    user_id = str(message.author.id)
    if user_id not in user_history:
        user_history[user_id] = []

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, CommandOnCooldown):
        seconds = round(error.retry_after + 0.5)
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {seconds} seconds.",
            ephemeral=True
        )



bot.run(os.environ.get('TOKEN'))
