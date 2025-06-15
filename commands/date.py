import discord
from discord import app_commands
import datetime
from commands.utils import cooldown

# Calculate days until Ocean+ anniversary
oplus_date = '2023-09-22'
today = datetime.date.today()
oplus = datetime.datetime.strptime(oplus_date, '%Y-%m-%d').date()
if oplus < today:
    oplus = datetime.date(today.year + 1, oplus.month, oplus.day)

days_until_oplus = (oplus - today).days

def setup(bot):
    """
    Register the date command with the bot
    """
    bot.tree.add_command(date_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="date", description="Get the current date and days until the next Ocean+ anniversary!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def date_command(interaction: discord.Interaction):
    # Recalculate today and days_until_oplus to ensure they're current
    today = datetime.date.today()
    oplus = datetime.datetime.strptime(oplus_date, '%Y-%m-%d').date()
    if oplus < today:
        oplus = datetime.date(today.year + 1, oplus.month, oplus.day)
    days_until_oplus = (oplus - today).days
    
    await interaction.response.send_message(f'Today is {today}!\nThere are {days_until_oplus} days until the next Ocean+ anniversary!')