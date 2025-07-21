import discord
from discord import app_commands
import io
import urllib.parse
import aiohttp
import os
from commands.utils import cooldown

jeyy_api = os.environ.get('JEYY_API')

def setup(bot):
    bot.tree.add_command(bonk_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="bonk", description="Bonk the mentioned user!")
@app_commands.describe(person="The person you want to bonk")
@app_commands.checks.dynamic_cooldown(cooldown)
async def bonk_command(interaction: discord.Interaction, person: discord.User):
    if not jeyy_api:
        await interaction.response.send_message("API key not configured!")
        return

    try:
        if not person.avatar:
            await interaction.response.send_message("User has no avatar!")
            return

        avatar_url = urllib.parse.quote(person.avatar.url)

        headers = {
            "Authorization": f"Bearer {jeyy_api}"
        }

        print(f"Attempting API request with token: {jeyy_api[:5]}...")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.jeyy.xyz/v2/image/bonks?image_url={avatar_url}",
                    headers=headers
            ) as response:
                if response.status == 401:
                    await interaction.response.send_message("API authentication failed. Please check API key.")
                    return
                elif response.status != 200:
                    error_text = await response.text()
                    await interaction.response.send_message(f"API Error {response.status}: {error_text}")
                    return

                image_data = await response.read()
                file = discord.File(io.BytesIO(image_data), filename="bonk.gif")
                await interaction.response.send_message(file=file)

    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")
        print(f"Detailed error: {str(e)}")