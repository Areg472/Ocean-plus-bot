import discord
from discord import app_commands
import requests
from typing import Optional
from commands.utils import cooldown

def setup(bot):
    """
    Register the weather command with the bot
    """
    bot.tree.add_command(weather_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="weather", description="Check the weather or the forecast for the specified location")
@app_commands.describe(location="The location to check the weather for", forecast="Whether to check the forecast or not")
@app_commands.checks.dynamic_cooldown(cooldown)
async def weather_command(interaction: discord.Interaction, location: str, forecast: Optional[bool] = False):
    response = requests.get("https://api.popcat.xyz/v2/weather?q=" + location)
    json_data = response.json()
    location = json_data['message'][0]['location']['name']
    temperature = json_data['message'][0]['current']['temperature']
    description = json_data['message'][0]['current']['skytext']
    feels_like = json_data['message'][0]['current']['feelslike']
    humidity = json_data['message'][0]['current']['humidity']
    wind_speed = json_data['message'][0]['current']['windspeed']
    tomorrow_high = json_data['message'][0]['forecast'][0]['high']
    tomorrow_low = json_data['message'][0]['forecast'][0]['low']
    tomorrow_description = json_data['message'][0]['forecast'][0]['skytextday']
    one_day_high = json_data['message'][0]['forecast'][1]['high']
    one_day_low = json_data['message'][0]['forecast'][1]['low']
    one_day_description = json_data['message'][0]['forecast'][1]['skytextday']
    two_day = json_data['message'][0]['forecast'][2]['day']
    two_day_high = json_data['message'][0]['forecast'][2]['high']
    two_day_low = json_data['message'][0]['forecast'][2]['low']
    two_day_description = json_data['message'][0]['forecast'][2]['skytextday']
    three_day = json_data['message'][0]['forecast'][3]['day']
    three_day_high = json_data['message'][0]['forecast'][3]['high']
    three_day_low = json_data['message'][0]['forecast'][3]['low']
    three_day_description = json_data['message'][0]['forecast'][3]['skytextday']
    four_day = json_data['message'][0]['forecast'][4]['day']
    four_day_high = json_data['message'][0]['forecast'][4]['high']
    four_day_low = json_data['message'][0]['forecast'][4]['low']
    four_day_description = json_data['message'][0]['forecast'][4]['skytextday']
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