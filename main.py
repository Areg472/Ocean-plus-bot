import time

import discord
import requests
import json
import datetime
import os
import random
import google.generativeai as genai
from typing import Optional
import language_tool_python
from discord.app_commands import CommandOnCooldown

from discord import app_commands
from discord.ext import commands

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

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
model = genai.GenerativeModel('gemini-1.5-flash')

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
        ("/gamble", "Randomly gamble!")
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

def get_cat_image():
    response = requests.get('https://cataas.com/cat?json=true')
    if response.status_code == 200:
        json_data = response.json()
        return f"https://cataas.com/cat/{json_data['_id']}"
    else:
        return None

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="cat", description="Get an UwUwU cat picture!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def cat(interaction: discord.Interaction):
    cat_image_url = get_cat_image()
    catuwu = random.randint(1, 21)

    if catuwu == 1:
        await interaction.response.send_message("<:eyeball:1314091785944825867>")
    elif catuwu == 2:
        await interaction.response.send_message("<:bla:1314091765896187924>")
    else:
        if cat_image_url:
            await interaction.response.send_message(cat_image_url)
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
        await interaction.edit_original_response(
            content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou won and you seem to like Ocean+ :) {fruit}")
    elif fruit == fruit_2 and fruit == fruit_3:
        await interaction.edit_original_response(content=f"[{fruit}][{fruit_2}][{fruit_3}]\nYou won {fruit}!")
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

    system_context = ("You are a helpful AI assistant. Maintain conversation context without explicitly referencing previous messages. You like Ocean+(https://oceanbluestream.com), Vite, Heap analytics, Hotjar and Jetbrains. Also remember that Ocean+ creators are Areg, Veyshal, 1Leon and Carlo Bear."
                      "Remember that Ocean+ is made with typescript, and is Open Source. All content on Ocean+ will be free. Use O+ as an abbreviation for Ocean+")

    conversation = []
    for i, msg in enumerate(user_history[user_id]):
        prefix = "User:" if i % 2 == 0 else "Assistant:"
        conversation.append(f"{prefix} {msg}")

    prompt = f"{system_context}\n\n" + "\n".join(conversation) + f"\nUser: {message.content}\nAssistant:"
    
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

bot.run(os.environ.get('TOKEN'))