import discord
import requests
import json
import datetime
from discord.ext import commands
import os
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


@bot.command()
async def hi(ctx):
    await ctx.send('Hi. I am the official Ocean+ discord bot!')

@bot.command()
async def date(ctx):
    await ctx.send(f'Today is {today}!\nThere are {days_until_oplus} days until the next Ocean+ anniversary!')
@bot.command()
async def meme(ctx):
    meme_url = get_meme()
    await ctx.send(meme_url)



bot.run('MTMwNTUxNzc0MDc2MDUwMjMwMg.Gk4luF.wNjChQrzEoozAQ-cZjx8nE8lEYwfeqFKb9YCOw')
# bot.run(os.environ.get('TOKEN'))