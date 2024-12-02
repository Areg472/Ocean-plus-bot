import discord
import requests
import json
import datetime
import os
from keep_alive import keep_alive

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

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == self.user:
      return
    if message.content.startswith('$meme'):
      await message.channel.send(get_meme())
    if message.content.startswith('$hi') or message.content.startswith('$hello')\
            or message.content.startswith('$hey') or message.content.startswith('$yo')\
            or message.content.startswith('$sup') or message.content.startswith('$hi!'):
        await message.channel.send('Hi. I am the official Ocean+ discord bot!')
    if message.content.startswith('$date'):
        await message.channel.send(f'Today is {today}!\n'
                                   f'There are {days_until_oplus} days until the next Ocean+ anniversary!')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.environ.get('TOKEN'))