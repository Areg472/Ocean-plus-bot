import discord
from discord import app_commands
import random
import time
from commands.utils import cooldown

def setup(bot):
    """
    Register the gamble command with the bot
    """
    bot.tree.add_command(gamble_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="gamble", description="Randomly gamble")
@app_commands.checks.dynamic_cooldown(cooldown)
async def gamble_command(interaction: discord.Interaction):
    fruit = random.randint(1, 7)
    if fruit == 1:
        fruit = "<:veyshal:1314896853195554847>"
    elif fruit == 2:
        fruit = "<:leon:1314896829531295786>"
    elif fruit == 3:
        fruit = "<:ocean_plus:1314896902449397760>"
    elif fruit == 4:
        fruit = "<:eyeball:1314091785944825867>"
    elif fruit == 5:
        fruit = "<:bla:1314091765896187924>"
    elif fruit == 6:
        fruit = "<a:duck_dance:1314847476548894771>"
    elif fruit == 7:
        fruit = "<:carlo:1314897409268256839>"
    await interaction.response.send_message(f"[{fruit}][      ][      ]")
    fruit_2 = random.randint(1, 7)
    if fruit_2 == 1:
        fruit_2 = "<:veyshal:1314896853195554847>"
    elif fruit_2 == 2:
        fruit_2 = "<:leon:1314896829531295786>"
    elif fruit_2 == 3:
        fruit_2 = "<:ocean_plus:1314896902449397760>"
    elif fruit_2 == 4:
        fruit_2 = "<:eyeball:1314091785944825867>"
    elif fruit_2 == 5:
        fruit_2 = "<:bla:1314091765896187924>"
    elif fruit_2 == 6:
        fruit_2 = "<a:duck_dance:1314847476548894771>"
    elif fruit_2 == 7:
        fruit_2 = "<:carlo:1314897409268256839>"
    time.sleep(1)
    await interaction.edit_original_response(content = f"[{fruit}][{fruit_2}][      ]")
    fruit_3 = random.randint(1, 7)
    if fruit_3 == 1:
        fruit_3 = "<:veyshal:1314896853195554847>"
    elif fruit_3 == 2:
        fruit_3 = "<:leon:1314896829531295786>"
    elif fruit_3 == 3:
        fruit_3 = "<:ocean_plus:1314896902449397760>"
    elif fruit_3 == 4:
        fruit_3 = "<:eyeball:1314091785944825867>"
    elif fruit_3 == 5:
        fruit_3 = "<:bla:1314091765896187924>"
    elif fruit_3 == 6:
        fruit_3 = "<a:duck_dance:1314847476548894771>"
    elif fruit_3 == 7:
        fruit_3 = "<:carlo:1314897409268256839>"
    time.sleep(1)
    await interaction.edit_original_response(content=f"[{fruit}][{fruit_2}][{fruit_3}]")
    if fruit == fruit_2 and fruit == fruit_3 and fruit == "<a:duck_dance:1314847476548894771>":
        time.sleep(0.5)
        await interaction.edit_original_response(content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou won and you're special! {fruit}")
    elif fruit == fruit_2 and fruit == fruit_3 and fruit == "<:ocean_plus:1314896902449397760>":
        time.sleep(0.5)
        await interaction.edit_original_response(
            content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou won and you seem to like Ocean+ :) {fruit}")
    elif fruit == fruit_2 and fruit == fruit_3:
        await interaction.edit_original_response(content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou won {fruit}!")
    elif fruit == fruit_2 or fruit == fruit_3 or fruit_2 == fruit_3:
        time.sleep(0.5)
        await interaction.edit_original_response(content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou won slightly!")
    else:
        time.sleep(0.5)
        await interaction.edit_original_response(content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou lost :(")