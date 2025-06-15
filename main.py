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
    # Basic debug - log every message
    print(f"BASIC DEBUG: Message received from {message.author.id} ({message.author.name}) in channel {message.channel.id}: '{message.content}'")
    
    from commands.generate_code import user_codes
    print(f"BASIC DEBUG: user_codes imported: {user_codes}")
    
    if message.author.bot:
        print("BASIC DEBUG: Message is from bot, ignoring")
        return
    
    print("BASIC DEBUG: Message is from a real user!")

    # TEMPORARY: Check for codes in ANY channel for testing
    print(f"BASIC DEBUG: Checking if {message.channel.id} == 1079639383445098587")
    if message.channel.id == 1079639383445098587:
        print("BASIC DEBUG: Message is in target channel!")
        user_id = message.author.id
        message_content = message.content.strip()
        
        print(f"Debug: Checking code for user {user_id}: '{message_content}'")
        print(f"Debug: Available codes: {user_codes}")
        print(f"Debug: User {user_id} in codes? {user_id in user_codes}")
        if user_id in user_codes:
            print(f"Debug: User's stored code: '{user_codes[user_id]}'")
            print(f"Debug: Message content: '{message_content}'")
            print(f"Debug: Codes match? {user_codes[user_id] == message_content}")
        
        if user_id in user_codes and user_codes[user_id] == message_content:
            print("Debug: CODE MATCH! Sending message...")
            # Send the Ocean+ link
            await message.channel.send(
                "<@1299815086147502080> https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB"
            )
            print(f"Debug: Code verified! Sent message for user {user_id}")
            del user_codes[user_id]
            print(f"Debug: Deleted code for user {user_id}")
        else:
            print("BASIC DEBUG: Code doesn't match or user has no code")
        return
    else:
        print(f"BASIC DEBUG: Message is NOT in target channel (it's in {message.channel.id})")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, CommandOnCooldown):
        seconds = round(error.retry_after + 0.5)
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {seconds} seconds.",
            ephemeral=True
        )



bot.run(os.environ.get('TOKEN'))
