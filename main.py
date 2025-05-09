import io
import time
import urllib
import discord
import requests
import json
import datetime
import os
import wikipediaapi
import random
import google.generativeai as genai
import aiohttp
import language_tool_python
from discord.app_commands import CommandOnCooldown
import logging
import xml.etree.ElementTree as ET
import time
import html
from typing import Optional

from discord import app_commands
from discord.ext import commands

from keep_alive import keep_alive

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.default()
intents.message_content = True

jeyy_api = os.environ.get('JEYY_API')

bot = commands.Bot(command_prefix='$', intents=intents)

keep_alive()

tool = language_tool_python.LanguageToolPublicAPI('en-US')

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
model = genai.GenerativeModel('gemini-2.0-flash')

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

def cooldown(interaction: discord.Interaction):
    return app_commands.Cooldown(1, 3.0)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="hi", description="Say hi to the bot!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def hi(interaction: discord.Interaction):
    await interaction.response.send_message('Hi. I am the official Ocean+ discord bot!')

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="meme", description="Send a funny meme!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def meme(interaction: discord.Interaction):
    meme_url = get_meme()
    wtf = random.randint(1, 19)
    if wtf == 1:
        await interaction.response.send_message("Errm What the Sigma?")
    elif wtf == 2:
        await interaction.response.send_message("Skibidi toilet sigma aura rizz fanum tax - no one")
    else:
        await interaction.response.send_message(meme_url)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="date", description="Get the current date and days until the next Ocean+ anniversary!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def date(interaction: discord.Interaction):
    await interaction.response.send_message(f'Today is {today}!\nThere are {days_until_oplus} days until the next Ocean+ anniversary!')

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="got_a_life", description="Check if you have a life or not")
@app_commands.checks.dynamic_cooldown(cooldown)
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
@app_commands.checks.dynamic_cooldown(cooldown)
async def quote(interaction: discord.Interaction):
    quote_text = get_quote()
    hmm = random.randint(1, 20)
    if hmm == 1:
        await interaction.response.send_message('"BRR SKIBIDI DOB DOB DOB OH YES YES YES." - not Areg')
    else:
        await interaction.response.send_message(quote_text)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="duck", description="Get an UwU duck picture")
@app_commands.checks.dynamic_cooldown(cooldown)
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
@app_commands.checks.dynamic_cooldown(cooldown)
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
@app_commands.checks.dynamic_cooldown(cooldown)
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
@app_commands.describe(text="The text to translate", target_language="The target language.")
@app_commands.checks.dynamic_cooldown(cooldown)
async def translate(interaction: discord.Interaction, text: str, target_language: Optional[str] = "en"):
    translation = get_translation(text, target_language)
    await interaction.response.send_message(translation)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="help", description="Help you out with commands!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def help(interaction: discord.Interaction):
    commands_list = [
        ("/quote", "Get a random quote"),
        ("/meme", "Get a random meme"),
        ("/date", "Get the current date and days until the next Ocean+ anniversary"),
        ("/got_a_life", "Check if you have a life or not"),
        ("/duck", "Get an UwU duck picture"),
        ("/dad_joke", "Generates a random dad joke"),
        ("/question", "Ask questions to Gemini!"),
        ("/translate", "Translate any text to any languages!"),
        ("/cat", "Sends a cute cat picture!"),
        ("/8ball", "Fortune teller!"),
        ("/mock", "Make your message wEirD aS hEll"),
        ("/weather", "Check the weather for the specified location or check forecast!"),
        ("/text_to_morse", "Translate text to morse code!"),
        ("/wanted", "Make a person wanted!"),
        ("Context menu command - Spelling Checker", "Check your spelling!"),
        ("/gamble", "Randomly gamble!"),
        ("/wikipedia", "Search wikipedia articles"),
        ("/pat", "Pat the mentioned user!"),
        ("/jail", "Put the mentioned user in jail!"),
        ("/github", "Get github info of a user"),
        ("/joke_overhead", "Use this and mention the guy that doesn't understand jokes!"),
        ("/bonk", "Bonk the mentioned person!"),
        ("/hi", "Say hi to the bot!"),
        ("/mute(Only in O+ server)", "Mute the mentioned user!"),
        ("/ban(Only in O+ server)", "Ban the mentioned user!"),
        ("/oplusadmin(Only in O+ server)", "Promote the mentioned user to Ocean+ admin!"),
    ]

    pages = []
    for i in range(0, len(commands_list), 6):
        page_commands = commands_list[i:i+6]
        embed = discord.Embed(
            title="Ocean+ Help",
            url="https://oceanbluestream.com/",
            description=f"Page {len(pages)+1}/{-(-len(commands_list)//6)}", 
            colour=discord.Colour.dark_blue()
        )

        for cmd, desc in page_commands:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.set_footer(text="Made by Areg, the creator of Ocean+. Thanks to Its_Padar for helping me with the code, make sure to give him a follow on BlueSky!")
        pages.append(embed)

    class HelpView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            self.current_page = 0

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = (self.current_page - 1) % len(pages)
            await interaction.response.edit_message(embed=pages[self.current_page])

        @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = (self.current_page + 1) % len(pages)
            await interaction.response.edit_message(embed=pages[self.current_page])

    view = HelpView()
    await interaction.response.send_message(embed=pages[0], view=view)

@bot.tree.command(name="cat", description="Get an UwUwU cat picture!")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.checks.dynamic_cooldown(cooldown)
async def cat(interaction: discord.Interaction):
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

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="8ball", description="A nice fortune teller")
@app_commands.describe(question="The question")
@app_commands.checks.dynamic_cooldown(cooldown)
async def eightball(interaction: discord.Interaction, question: str):
    the_guesser = random.randint(1, 100)
    response = requests.get("https://api.popcat.xyz/8ball")
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
        answer = json_data['answer']
    the_response = discord.Embed(title="8ball", colour=discord.Colour.dark_blue()).add_field(
        name="Question", value=f"The question is: {question}", inline=False).add_field(
        name="Answer", value=f"The answer is: {answer}", inline=False).set_thumbnail(
        url="https://utfs.io/f/thKihuQxhYcPMVYP3wSWO0gf3VwBDZHjFudhtIEoAaeUXbx2")
    await interaction.response.send_message(embed=the_response)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="mock", description="Make your message wEirD aS hEll")
@app_commands.describe(message="The message to mock")
@app_commands.checks.dynamic_cooldown(cooldown)
async def mock(interaction: discord.Interaction, message: str):
    response = requests.get("https://api.popcat.xyz/mock?text=" + message)
    json_data = response.json()
    await interaction.response.send_message(json_data['text'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="weather", description="Check the weather or the forecast for the specified location")
@app_commands.describe(location="The location to check the weather for", forecast="Whether to check the forecast or not")
@app_commands.checks.dynamic_cooldown(cooldown)
async def weather(interaction: discord.Interaction, location: str, forecast: Optional[bool] = False):
    response = requests.get("https://api.popcat.xyz/weather?q=" + location)
    json_data = response.json()
    location = json_data[0]['location']['name']
    temperature = json_data[0]['current']['temperature']
    description = json_data[0]['current']['skytext']
    feels_like = json_data[0]['current']['feelslike']
    humidity = json_data[0]['current']['humidity']
    wind_speed = json_data[0]['current']['windspeed']
    tomorrow_high = json_data[0]['forecast'][0]['high']
    tomorrow_low = json_data[0]['forecast'][0]['low']
    tomorrow_description = json_data[0]['forecast'][0]['skytextday']
    one_day_high = json_data[0]['forecast'][1]['high']
    one_day_low = json_data[0]['forecast'][1]['low']
    one_day_description = json_data[0]['forecast'][1]['skytextday']
    two_day = json_data[0]['forecast'][2]['day']
    two_day_high = json_data[0]['forecast'][2]['high']
    two_day_low = json_data[0]['forecast'][2]['low']
    two_day_description = json_data[0]['forecast'][2]['skytextday']
    three_day = json_data[0]['forecast'][3]['day']
    three_day_high = json_data[0]['forecast'][3]['high']
    three_day_low = json_data[0]['forecast'][3]['low']
    three_day_description = json_data[0]['forecast'][3]['skytextday']
    four_day = json_data[0]['forecast'][4]['day']
    four_day_high = json_data[0]['forecast'][4]['high']
    four_day_low = json_data[0]['forecast'][4]['low']
    four_day_description = json_data[0]['forecast'][4]['skytextday']
    if forecast == True:
        weather_data = discord.Embed(title=f"Weather of {location}!", colour=discord.Colour.dark_blue()).add_field(
            name="Current temperature", value=f"{temperature}°C \nFeels like: {feels_like}°C \n{description}", inline=True).add_field(
            name="Today's temperature", value=f"High: {tomorrow_high}°C \nLow {tomorrow_low}°C \n{tomorrow_description}", inline=True).add_field(
            name=f"Tomorrow's temperature", value=f"High: {one_day_high}°C \nLow: {one_day_low}°C \n{one_day_description}", inline=True).add_field(
            name=f"{two_day}'s temperature", value=f"High: {two_day_high}°C \nLow: {two_day_low}°C \n{two_day_description}", inline=True).add_field(
            name=f"{three_day}'s temperature", value=f"High: {three_day_high}°C \nLow: {three_day_low}°C \n{three_day_description}", inline=True).add_field(
            name=f"{four_day}'s temperature", value=f"High: {four_day_high}°C \nLow: {four_day_low}°C \n{four_day_description}", inline=True)
    elif forecast == False:
        weather_data = discord.Embed(title=f"Weather of {location}!", colour=discord.Colour.dark_blue()).add_field(
            name="Temperature", value=f"{temperature}°C, {description}", inline=False).add_field(
            name="Feels Like", value=f"{feels_like}°C", inline=False).add_field(
            name="Humidity", value=f"{humidity}%", inline=False).add_field(
            name="Wind Speed", value=f"The speed is: {wind_speed}", inline=False)

    await interaction.response.send_message(embed=weather_data)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="text_to_morse", description="Translate text to morse")
@app_commands.describe(text="The text to translate")
@app_commands.checks.dynamic_cooldown(cooldown)
async def text_to_morse(interaction: discord.Interaction, text: str):
    response = requests.get(f"https://api.popcat.xyz/texttomorse?text={text}")
    json_data = response.json()
    morse_text = json_data['morse']
    morse_embed = discord.Embed(title="Text to Morse", colour=discord.Colour.dark_blue()).add_field(
        name="Original", value=text, inline=False).add_field(
        name="Morse", value=morse_text, inline=False)
    await interaction.response.send_message(embed=morse_embed)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="wanted", description="Make a person wanted!")
@app_commands.describe(person="The person you wanted")
@app_commands.checks.dynamic_cooldown(cooldown)
async def wanted(interaction: discord.Interaction, person: discord.User):
    avatar_url = person.avatar.url
    response = requests.get(f"https://api.popcat.xyz/wanted?image={avatar_url}")
    await interaction.response.send_message(response.url)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name="Spelling Checker")
async def spelling(interaction: discord.Interaction, message: discord.Message):
    text = str(message.content)
    suggest = tool.correct(text)
    await interaction.response.send_message(f'Errm did you mean "{suggest}"?')

bot.tree.add_command(spelling)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="gamble", description="Randomly gamble")
@app_commands.checks.dynamic_cooldown(cooldown)
async def gamble(interaction: discord.Interaction):
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

user_history = {}
MAX_HISTORY = 30

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id != 1315586087573258310:
        return

    user_id = str(message.author.id)
    if user_id not in user_history:
        user_history[user_id] = []

    system_context = ("You are a helpful AI assistant. Maintain conversation context without explicitly referencing previous messages. You like Ocean+ https://oceanbluestream.com, Vite, Heap analytics, Betterstack, Datadog, Github, Netlify, Hotjar and Jetbrains. Also remember that Ocean+ creators are Areg, Veyshal, 1Leon and Carlo Bear."
                      "Remember that Ocean+ is made with typescript, and is Open Source. All content on Ocean+ will be free. Use O+ as an abbreviation for Ocean+ in long sentences. Ocean+ is a free Vyond and GoAnimate movie streaming service. Use emojis a bit more. Don't promote Ocean+ on every message unless requested to but promote it like every 10th message."
                      "1+1 is 2.")

    conversation = []
    for i, msg in enumerate(user_history[user_id]):
        prefix = "User:" if i % 2 == 0 else "Assistant:"
        conversation.append(f"{prefix} {msg}")

    prompt = f"{system_context}\n\n" + "\n".join(conversation) + f"\nUser: {message.content}\nAssistant:"

    if user_id == "":
        await message.channel.send("<:bla:1314091765896187924>")
    else:
        response = await get_gemini_response(prompt)

        if response:
            user_history[user_id].append(message.content)
            user_history[user_id].append(response)
            user_history[user_id] = user_history[user_id][-MAX_HISTORY:]
            await message.channel.send(response)
        else:
            await message.channel.send("Sorry, I couldn't generate a response at this time.")

        await bot.process_commands(message)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, CommandOnCooldown):
        seconds = round(error.retry_after + 0.5)
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {seconds} seconds.",
            ephemeral=True
        )


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="wikipedia", description="Search wikipedia articles")
@app_commands.describe(query="The search query")
@app_commands.checks.dynamic_cooldown(cooldown)
async def wiki_search(interaction: discord.Interaction, query: str):
    wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent='DiscordBot/1.0'
    )

    try:
        page = wiki.page(query)

        if page.exists():
            if page.summary <= page.summary[:500]:
                embed = discord.Embed(
                    title=page.title,
                    url=page.fullurl,
                    description=page.summary,
                    color=discord.Color.blue()
                )
            elif page.summary > page.summary[:500]:
                embed = discord.Embed(
                    title=page.title,
                    url=page.fullurl,
                    description=page.summary[:500] + "...",
                    color=discord.Color.blue()
                )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"Could not find Wikipedia article for '{query}'")

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="bonk", description="Bonk the mentioned user!")
@app_commands.describe(person="The person you want to bonk")
@app_commands.checks.dynamic_cooldown(cooldown)
async def bonk(interaction: discord.Interaction, person: discord.User):
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


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="pat", description="Pat the mentioned user!")
@app_commands.describe(person="The person you want to pat")
@app_commands.checks.dynamic_cooldown(cooldown)
async def pat(interaction: discord.Interaction, person: discord.User):
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
                f"https://api.jeyy.xyz/v2/image/patpat?image_url={avatar_url}", 
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
                file = discord.File(io.BytesIO(image_data), filename="pet.gif")
                await interaction.response.send_message(file=file)

    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")
        print(f"Detailed error: {str(e)}")


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="jail", description="Put the mentioned user in jail!")
@app_commands.describe(person="The person you want to go to jail!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def jail(interaction: discord.Interaction, person: discord.User):
    avatar_url = person.avatar.url
    response = requests.get(f"https://api.popcat.xyz/jail?image={avatar_url}")
    await interaction.response.send_message(response.url)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="joke_overhead", description="Use this and mention the guy that doesn't understand jokes!")
@app_commands.describe(the_guy="The guy that doesn't understand jokes")
@app_commands.checks.dynamic_cooldown(cooldown)
async def joke_overhead(interaction: discord.Interaction, the_guy: discord.User):
    avatar_url = the_guy.avatar.url + ".png"
    response = requests.get(f"https://api.popcat.xyz/jokeoverhead?image={avatar_url}")
    await interaction.response.send_message(response.url)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="github", description="Get github info of a user")
@app_commands.describe(username="The username you want to get github info of")
@app_commands.checks.dynamic_cooldown(cooldown)
async def github(interaction: discord.Interaction, username: str):
    response = requests.get(f"https://api.popcat.xyz/github/{username}")
    json_data = response.json()
    github_name = json_data['name']
    github_url = json_data['url']
    github_avatar = json_data['avatar']
    github_location = json_data['location']
    github_bio = json_data['bio']
    result = discord.Embed(title=f"Github info of {github_name}!", colour=discord.Colour.dark_blue()).add_field(
        name="Name", value=github_name, inline=False).add_field(
        name="Location", value=github_location, inline=False).add_field(
        name="Bio", value=github_bio, inline=False).add_field(
        name="Github URL", value=github_url, inline=False).set_thumbnail(
        url=github_avatar)
    await interaction.response.send_message(embed=result)

@bot.tree.command(name="mute", description="Mute someone!")
@app_commands.checks.dynamic_cooldown(cooldown)
@app_commands.describe(
    user="The user you want to mute",
    reason="The reason for the mute",
    duration="The duration of the mute (in minutes)"
)
async def mute(interaction: discord.Interaction, user: discord.Member, duration: int, reason: Optional[str] = None):
    guildID = interaction.guild.id
    if guildID != 1183318046866149387:
        await interaction.response.send_message("This command is only available in the Ocean+ server!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You do not have permission to mute members.", ephemeral=True)
        return

    if duration <= 0:
        await interaction.response.send_message("Duration must be positive!", ephemeral=True)
        return

    try:
        reason_text = reason or "No reason provided"
        await user.timeout(datetime.timedelta(minutes=duration), reason=reason_text)

        await interaction.response.send_message(
            f"✅ {user.mention} has been muted for {duration} minutes.\nReason: {reason_text}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to mute this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="ban", description="Ban someone!")
@app_commands.checks.dynamic_cooldown(cooldown)
@app_commands.describe(
    user="The user you want to ban",
    reason="The reason for the ban",
    delete_days="The messages you want to be deleted in days."
)
async def ban(interaction: discord.Interaction, user: discord.Member, delete_days: Optional[int] = None, reason: Optional[str] = None):
    guildID = interaction.guild.id
    if guildID != 1183318046866149387:
        await interaction.response.send_message("This command is only available in the Ocean+ server!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You do not have permission to ban members.", ephemeral=True)
        return

    if delete_days is not None and (delete_days < 0 or delete_days > 7):
        await interaction.response.send_message("Delete days must be between 0 and 7!", ephemeral=True)
        return

    try:
        reason_text = reason or "No reason provided"
        await user.ban(delete_message_days=delete_days, reason=reason_text)
        await interaction.response.send_message(
            f"✅ {user.mention} has been banned.\nReason: {reason_text}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="oplusadmin", description="Make someone an O+ admin!")
@app_commands.checks.dynamic_cooldown(cooldown)
@app_commands.describe(
    user="The user you want to make an admin",
    reason="The reason for the promotion",
)
async def oplusadmin(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return

    guildID = interaction.guild.id
    if guildID != 1183318046866149387:
        await interaction.response.send_message("This command is only available in the Ocean+ server!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You need manage roles permissions to make people O+ admins.", ephemeral=True)
        return

    try:
        role = discord.utils.get(interaction.guild.roles, name="Ocean+ admin")
        if not role:
            await interaction.response.send_message("The Ocean+ admin role could not be found!", ephemeral=True)
            return

        if role in user.roles:
            await interaction.response.send_message(f"{user.mention} is already an Ocean+ Admin!", ephemeral=True)
            return

        await user.add_roles(role)
        reason_text = reason or "No reason provided"
        await interaction.response.send_message(
            f"✅ {user.mention} has been made an Ocean+ Admin.\nReason: {reason_text}",
            ephemeral=False
        )

    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to manage roles!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


class BoardGameView(discord.ui.View):
    def __init__(self, embeds, author):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.author = author
        self.current_page = 0
        
        if len(embeds) <= 1:
            for child in self.children:
                child.disabled = True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        try:
            await self.message.edit(view=self)
        except:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the person who ran this command can use these buttons.",
                                                    ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="boardgame", description="Search for board games on BoardGameGeek")
@app_commands.describe(query="The name of the board game to search for")
@app_commands.checks.dynamic_cooldown(cooldown)
async def boardgame(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    try:
        search_url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"
        response = requests.get(search_url)

        if response.status_code != 200:
            await interaction.followup.send(
                f"Error: Could not connect to BoardGameGeek API. Status code: {response.status_code}")
            return

        root = ET.fromstring(response.content)
        items = root.findall('.//item')

        if not items:
            await interaction.followup.send(f"No board games found matching '{query}'.")
            return

        items = items[:15]
        total_results = len(items)

        game_ids = [item.get('id') for item in items]
        details_url = f"https://boardgamegeek.com/xmlapi2/thing?id={','.join(game_ids)}&stats=1"
        details_response = requests.get(details_url)

        if details_response.status_code == 202:
            await interaction.followup.send("Processing your request... Please try again in a few seconds.",
                                            ephemeral=True)
            time.sleep(2)
            details_response = requests.get(details_url)

        if details_response.status_code != 200:
            await interaction.followup.send(
                f"Error: Could not retrieve game details. Status code: {details_response.status_code}")
            return

        details_root = ET.fromstring(details_response.content)
        game_details = {}

        for item in details_root.findall('.//item'):
            game_id = item.get('id')
            description = item.find('.//description')
            description_text = description.text if description is not None and description.text else "No description available."
            
            # Decode HTML entities in the description
            description_text = html.unescape(description_text)

            if len(description_text) > 200:
                description_text = description_text[:197] + "..."

            rating_element = item.find('.//statistics/ratings/average')
            rating = rating_element.get('value') if rating_element is not None else "N/A"

            min_players_element = item.find('.//minplayers')
            max_players_element = item.find('.//maxplayers')
            min_players = min_players_element.get('value') if min_players_element is not None else "?"
            max_players = max_players_element.get('value') if max_players_element is not None else "?"

            playtime_element = item.find('.//playingtime')
            playtime = playtime_element.get('value') if playtime_element is not None else "?"

            game_details[game_id] = {
                'description': description_text,
                'rating': rating,
                'players': f"{min_players}-{max_players}" if min_players != max_players else min_players,
                'playtime': playtime
            }

        embeds = []

        if total_results <= 5:
            embed = discord.Embed(
                title=f" BoardGameGeek Search Results for '{query}'",
                color=discord.Color.blue(),
                description=f"Found {total_results} result(s)"
            )

            for item in items:
                game_id = item.get('id')
                name_element = item.find('name')
                game_name = html.unescape(name_element.get('value')) if name_element is not None else "Unknown"
                year_published = item.find('yearpublished')
                year = year_published.get('value') if year_published is not None else "N/A"

                bgg_link = f"https://boardgamegeek.com/boardgame/{game_id}"

                if game_id in game_details:
                    details = game_details[game_id]
                    description = details['description']
                    info_line = f"⭐ {details['rating']}/10 •  {details['players']} players • ⏱️ {details['playtime']} min"
                    value_text = f"{description}\n\n{info_line}\n[View on BoardGameGeek]({bgg_link})"
                else:
                    value_text = f"[View on BoardGameGeek]({bgg_link})"

                embed.add_field(
                    name=f"{game_name} ({year})",
                    value=value_text,
                    inline=False
                )

            embed.set_footer(text="Data from BoardGameGeek")
            embeds.append(embed)
        else:
            for page in range((total_results + 4) // 5):
                start_idx = page * 5
                end_idx = min(start_idx + 5, total_results)
                page_items = items[start_idx:end_idx]

                embed = discord.Embed(
                    title=f" BoardGameGeek Search Results for '{query}'",
                    color=discord.Color.blue(),
                    description=f"Found {total_results} result(s)"
                )

                for item in page_items:
                    game_id = item.get('id')
                    name_element = item.find('name')
                    game_name = html.unescape(name_element.get('value')) if name_element is not None else "Unknown"
                    year_published = item.find('yearpublished')
                    year = year_published.get('value') if year_published is not None else "N/A"

                    bgg_link = f"https://boardgamegeek.com/boardgame/{game_id}"

                    if game_id in game_details:
                        details = game_details[game_id]
                        description = details['description']
                        info_line = f"⭐ {details['rating']}/10 •  {details['players']} players • ⏱️ {details['playtime']} min"
                        value_text = f"{description}\n\n{info_line}\n[View on BoardGameGeek]({bgg_link})"
                    else:
                        value_text = f"[View on BoardGameGeek]({bgg_link})"

                    embed.add_field(
                        name=f"{game_name} ({year})",
                        value=value_text,
                        inline=False
                    )

                embed.set_footer(text=f"Page {page + 1}/{(total_results + 4) // 5} • Data from BoardGameGeek")
                embeds.append(embed)

        view = BoardGameView(embeds, interaction.user)
        message = await interaction.followup.send(embed=embeds[0], view=view)
        view.message = message

    except Exception as e:
        await interaction.followup.send(f"An error occurred while searching for board games: {str(e)}")

bot.run(os.environ.get('TOKEN'))
