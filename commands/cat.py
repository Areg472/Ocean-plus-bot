import discord
from discord import app_commands
import aiohttp
import random
from commands.utils import cooldown

def setup(bot):
    """
    Register the cat command with the bot
    """
    bot.tree.add_command(cat_command)

@app_commands.command(name="cat", description="Get an UwUwU cat picture!")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.checks.dynamic_cooldown(cooldown)
async def cat_command(interaction: discord.Interaction):
    catuwu = random.randint(1, 21)

    if catuwu == 1:
        await interaction.response.send_message("<:eyeball:1314091785944825867>")
    elif catuwu == 2:
        await interaction.response.send_message("<:bla:1314091765896187924>")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                if response.status == 200:
                    json_data = await response.json()
                    await interaction.response.send_message(json_data[0]['url'])
                else:
                    await interaction.response.send_message("Could not fetch a cat image at this time.")