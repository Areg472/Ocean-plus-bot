import discord
from discord import app_commands
import requests
import random
from commands.utils import cooldown

def setup(bot):
    """
    Register the eightball command with the bot
    """
    bot.tree.add_command(eightball_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="8ball", description="A nice fortune teller")
@app_commands.describe(question="The question")
@app_commands.checks.dynamic_cooldown(cooldown)
async def eightball_command(interaction: discord.Interaction, question: str):
    the_guesser = random.randint(1, 100)
    response = requests.get("https://api.popcat.xyz/v2/8ball")
    json_data = response.json()
    if the_guesser == 1:
        answer = "Yes."
    elif the_guesser == 2:
        answer = "No."
    elif the_guesser == 3:
        answer = "Maybe, but I'm sober."
    elif the_guesser == 4:
        answer = "AMOGUS"
    elif the_guesser == 5:
        answer = "I don't know, ask Areg."
    elif the_guesser == 6:
        answer = "I like u UwU"
    elif the_guesser == 7:
        answer = "CPU - 99% Heat - 120 Celsius"
    elif the_guesser == 8:
        answer = "leave me alone!"
    elif the_guesser == 9:
        answer = "I will send you to Armenia!"
    elif the_guesser == 10:
        answer = "I'm a bot, I don't know."
    elif the_guesser == 11:
        answer = "I'm a machine that turns you into broken code!"
    elif the_guesser == 12:
        answer = "I am UwU, OwO"
    elif the_guesser == 13:
        answer = "Skibidi toilet"
    else:
        answer = json_data['message']['answer']
    the_response = discord.Embed(title="8ball", colour=discord.Colour.dark_blue()).add_field(
        name="Question", value=f"The question is: {question}", inline=False).add_field(
        name="Answer", value=f"The answer is: {answer}", inline=False).set_thumbnail(
        url="https://utfs.io/f/thKihuQxhYcPMVYP3wSWO0gf3VwBDZHjFudhtIEoAaeUXbx2")
    await interaction.response.send_message(embed=the_response)