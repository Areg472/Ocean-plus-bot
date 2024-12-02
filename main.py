import discord
import requests
import json
import datetime
import os
import random

from discord.app_commands import describe
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

keep_alive()

def get_meme():
    response = requests.get('https://meme-api.com/gimme')
    json_data = json.loads(response.text)
    return json_data['url']

oplus_date = '2023-09-22'
today = datetime.date.today()
oplus = datetime.datetime.strptime(oplus_date, '%Y-%m-%d').date()
if oplus < today:
    oplus = datetime.date(today.year + 1, oplus.month, oplus.day)

days_until_oplus = (oplus - today).days

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

@bot.tree.command(name="hi", description="Say hi to the bot!")
async def hi(interaction: discord.Interaction):
    await interaction.response.send_message('Hi. I am the official Ocean+ discord bot!')

@bot.tree.command(name="meme", description="Send a funny meme!")
async def meme(interaction: discord.Interaction):
    meme_url = get_meme()
    await interaction.response.send_message(meme_url)

@bot.tree.command(name="date", description="Get the current date and days until the next Ocean+ anniversary!")
async def date(interaction: discord.Interaction):
    await interaction.response.send_message(f'Today is {today}!\nThere are {days_until_oplus} days until the next Ocean+ anniversary!')

@bot.tree.command(name="got_a_life", description="Check if you have a life or not")
async def got_a_life(interaction: discord.Interaction):
    life_check = random.choices([0, 1], weights=[75, 25], k=1)[0]
    message = "You have a life!" if life_check == 1 else "You don't have a life!"
    await interaction.response.send_message(message)


bot.run(os.environ.get('TOKEN'))