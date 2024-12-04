import discord
import requests
import json
import datetime
import os
import random
import google.generativeai as genai
from typing import Optional

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

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

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


async def get_gemini_response(question: str) -> Optional[str]:
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return None


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="question", description="Ask me anything, powered by Gemini")
@app_commands.describe(query = "What's the question? Be concise!")
async def question(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    answer = await get_gemini_response(query)
    if answer:
        if len(answer) > 2000:
            chunks = [answer[i:i + 1900] for i in range(0, len(answer), 1900)]
            for chunk in chunks:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(answer)
    else:
        await interaction.followup.send("Sorry, I couldn't generate a response at this time.")


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="dad_joke", description="Generates a random dad joke!")
async def dad_joke(interaction: discord.Interaction):
    response = requests.get("https://api.popcat.xyz/joke")
    json_data = response.json()
    nothing = random.randint(1, 20)
    if nothing == 1:
        await interaction.response.send_message('"Why does Areg break this bot a lot? Because he is broken."')
    else:
        await interaction.response.send_message(f"\"{json_data['joke']}\"")

def get_translation(text, target_language):
    response = requests.get(f'https://api.popcat.xyz/translate?to={target_language}&text={text}')
    if response.status_code == 200:
        json_data = response.json()
        return json_data['translated']
    else:
        return "Could not fetch the translation at this time."

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="translate", description="Translate text to a specified language")
@app_commands.describe(text="The text to translate", target_language="The target language code (e.g., 'en' for English)")
async def translate(interaction: discord.Interaction, text: str, target_language: Optional[str] = "en"):
    translation = get_translation(text, target_language)
    await interaction.response.send_message(translation)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="help", description="Help you out with commands!")
async def help(interaction: discord.Interaction):
    embed_help = discord.Embed(title="Ocean+ Help", url="https://oceanbluestream.com/", description="This is all you need for help with the commands!", colour=discord.Colour.dark_blue()).add_field(name="/quote", value="Get a random quote", inline=False).add_field(name="/meme", value="Get a random meme", inline=False).add_field(name="/date", value="Get the current date and days until the next Ocean+ anniversary", inline=False).add_field(name="/got_a_life", value="Check if you have a life or not", inline=False).add_field(name="/duck", value="Get an UwU duck picture", inline=False).add_field(name="/dad_joke", value="Generates a random dad joke", inline=False).add_field(name="/question", value="Ask questions to Gemini!", inline=False).add_field(name="/translate", value="Translate any text to any languages!").set_footer(text="Made by Areg, the creator of Ocean+. Thanks to Its_Padar for helping me with the code, make sure to give him a follow on BlueSky!")
    await interaction.response.send_message(embed=embed_help)

bot.run(os.environ.get('TOKEN'))