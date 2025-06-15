import discord
from discord import app_commands
from commands.utils import cooldown
import secrets
import string
import asyncio

# Dictionary to store user codes
user_codes = {}

async def reset_user_code(user_id, delay=30):
    """Reset a user's code after the specified delay (in seconds)"""
    await asyncio.sleep(delay)
    if user_id in user_codes:
        del user_codes[user_id]

def generate_user_code():
    """Generate a random 12-character alphanumeric code"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

def setup(bot):
    """
    Register the generate_code command with the bot
    """
    bot.tree.add_command(generate_code_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(dms=True, private_channels=True)  # DM only
@app_commands.command(name="generate_code", description="Generate a unique code for Ocean+ access!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def generate_code_command(interaction: discord.Interaction):
    # Generate a new code for this user
    user_id = interaction.user.id
    new_code = generate_user_code()
    user_codes[user_id] = new_code
    
    # Start the 30-second timer to reset the code
    asyncio.create_task(reset_user_code(user_id, 30))
    
    await interaction.response.send_message(
        f"🔑 **Your Ocean+ access code:** `{new_code}`\n\n"
        f"Use this code in the designated channel to get your Ocean+ link!\n"
        f"*Note: This code is unique to you and will expire in 30 seconds or after use.*",
        ephemeral=True
    )
