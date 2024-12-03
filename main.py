import discord
import requests
import json
import datetime
import os
import random

from discord import app_commands
from discord.ext import commands

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

keep_alive()

def get_meme():
    while True:
        response = requests.get('https://meme-api.com/gimme')
        json_data = json.loads(response.text)
        if not json_data.get('nsfw', True):
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


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="hi", description="Say hi to the bot!")
async def hi(interaction: discord.Interaction):
    await interaction.response.send_message('Hi. I am the official Ocean+ discord bot!')

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="meme", description="Send a funny meme!")
async def meme(interaction: discord.Interaction):
    meme_url = get_meme()
    wtf = random.randint(1, 19)
    if wtf == 1:
        await interaction.response.send_message("Errm What the Sigma?")
    elif wtf == 2:
        await interaction.response.send_message("Skibidi toilet sigma aura rizz - no one")
    else:
        await interaction.response.send_message(meme_url)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="date", description="Get the current date and days until the next Ocean+ anniversary!")
async def date(interaction: discord.Interaction):
    await interaction.response.send_message(f'Today is {today}!\nThere are {days_until_oplus} days until the next Ocean+ anniversary!')

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="got_a_life", description="Check if you have a life or not")
async def got_a_life(interaction: discord.Interaction):
    life_check = random.choices([0, 1], weights=[75, 25], k=1)[0]
    message = "You have a life!" if life_check == 1 else "You don't have a life!"
    await interaction.response.send_message(message)

def get_quote():
    try:
        response = requests.get('http://api.quotable.io/random')
        response.raise_for_status()
        json_data = response.json()
        return f'"{json_data["content"]}" - {json_data["author"]}'
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Could not fetch a quote at this time."

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="quote", description="Send a random quote!")
async def quote(interaction: discord.Interaction):
    quote_text = get_quote()
    hmm = random.randint(1, 20)
    if hmm == 7:
        await interaction.response.send_message('"BRR SKIBIDI DOB DOB DOB OH YES YES YES." - not Areg')
    else:
        await interaction.response.send_message(quote_text)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="duck", description="Get an UwU duck picture")
async def duck(interaction: discord.Interaction):
    response = requests.get("https://random-d.uk/api/random")
    json_data = response.json()
    hmmmmmm = random.randint(1, 20)
    if hmmmmmm == 1:
        await interaction.response.send_message("<:duck:1313390002805411872>")
    else:
        await interaction.response.send_message(json_data['url'])

def get_wanted_image(avatar_url):
    response = requests.get(f'https://api.popcat.xyz/wanted?image={avatar_url}')
    if response.status_code == 200:
        return response.url
    else:
        return None

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="wanted", description="Create a wanted image with the mentioned user.")
async def wanted(interaction: discord.Interaction, member: discord.Member):
    avatar_url = member.avatar.url
    wanted_image_url = get_wanted_image(avatar_url)
    if wanted_image_url:
        await interaction.response.send_message(wanted_image_url)
    else:
        await interaction.response.send_message("Could not create a wanted image at this time.")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="help", description="Help you out with commands!")
async def help(interaction: discord.Interaction):
    embed_help = discord.Embed(title="Ocean+ Help", url="https://oceanbluestream.com/", description="This is all you need for help with the commands!", colour=discord.Colour.dark_blue()).add_field(name="/quote", value="Get a random quote", inline=False).add_field(name="/meme", value="Get a random meme", inline=False).add_field(name="/date", value="Get the current date and days until the next Ocean+ anniversary", inline=False).add_field(name="/got_a_life", value="Check if you have a life or not", inline=False).add_field(name="/duck", value="Get an UwU duck picture", inline=False).add_field(name="/wanted", value="Create a wanted image with the mentioned user's avatar", inline=False)
    await interaction.response.send_message(embed=embed_help)


bot.run(os.environ.get('TOKEN'))