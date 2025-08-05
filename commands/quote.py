import discord
from discord import app_commands
import requests
import random
from commands.utils import cooldown

def get_quote():
    try:
        response = requests.get('https://zenquotes.io/api/random')
        response.raise_for_status()
        json_data = response.json()
        return f'"{json_data[0]["q"]}" - {json_data[0]["a"]}'
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Could not fetch a quote at this time."

def setup(bot):
    bot.tree.add_command(quote_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="quote", description="Send a random quote!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def quote_command(interaction: discord.Interaction):
    quote_text = get_quote()
    hmm = random.randint(1, 20)
    if hmm == 1:
        await interaction.response.send_message('"._." - not Areg')
    else:
        await interaction.response.send_message(quote_text)