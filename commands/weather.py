import discord
from discord import app_commands
import requests
from typing import Optional
from commands.utils import cooldown, get_ai_response

def get_user_instructions(user_id: int) -> str:
    user_specific_instructions = {
        1299815086147502080: "This user's name is whiplash. When summarizing the weather, compare the conditions, if it's good for going out to Tim Hortons, and if it's great weather to avoid Taco Bell",
        960524267164930128: "This user's name is Areg. When summarizing the weather, compare the conditions, if it's good for going out to Tim Hortons, and if it's great weather to avoid Taco Bell",
    }
    return user_specific_instructions.get(user_id, "")

class WeatherSummaryView(discord.ui.View):
    def __init__(self, weather_data: dict, location: str, include_forecast: bool = True):
        super().__init__(timeout=300)
        self.weather_data = weather_data
        self.location = location
        self.include_forecast = include_forecast
    
    @discord.ui.button(label="AI Weather Summary", style=discord.ButtonStyle.secondary, emoji="🤖")
    async def weather_summary(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        current = self.weather_data['message'][0]['current']
        
        weather_prompt = f"""Analyze this weather data for {self.location} and provide a concise, helpful summary:

Current Weather:
- Temperature: {current['temperature']}°C (feels like {current['feelslike']}°C)
- Condition: {current['skytext']}
- Humidity: {current['humidity']}%
- Wind Speed: {current['windspeed']}
"""
        
        if self.include_forecast:
            forecast_data = self.weather_data['message'][0]['forecast']
            weather_prompt += "\n5-Day Forecast:\n"
            
            for i, day in enumerate(forecast_data[:5]):
                day_name = "Today" if i == 0 else ("Tomorrow" if i == 1 else day['day'])
                weather_prompt += f"- {day_name}: High {day['high']}°C, Low {day['low']}°C - {day['skytextday']}\n"
            
            weather_prompt += "\nProvide insights about the weather pattern, any notable changes, and practical advice for the upcoming days. Keep it under 1500 characters."
        else:
            weather_prompt += "\nProvide insights about the current weather conditions and practical advice for today. Keep it under 1000 characters."

        waiting_embed = discord.Embed(
            title="🤔 Analyzing weather...",
            description="Generating AI weather summary with Mistral...",
            color=0x4285f4
        )
        waiting_message = await interaction.followup.send(embed=waiting_embed, ephemeral=True)
        
        try:
            user_instructions = get_user_instructions(interaction.user.id)
            
            ai_response = await get_ai_response(
                question=weather_prompt,
                model="mistral-small-2506",
                instructions=user_instructions
            )
            
            if isinstance(ai_response, tuple):
                summary_text = ai_response[0]
            else:
                summary_text = ai_response
                
            summary_embed = discord.Embed(
                title=f"AI Weather Summary for {self.location}",
                description=summary_text,
                colour=discord.Colour.green()
            )
            summary_embed.set_footer(text="Powered by Mistral AI")
            
            await waiting_message.edit(embed=summary_embed)
            
        except Exception as e:
            print(f"Weather AI summary error for user {interaction.user.id}: {str(e)}")
            error_embed = discord.Embed(
                title="Summary Error",
                description="Sorry, I couldn't generate a weather summary at the moment. Please try again later.",
                colour=discord.Colour.red()
            )
            await waiting_message.edit(embed=error_embed)

def setup(bot):
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
    view = WeatherSummaryView(json_data, location, forecast)
    await interaction.response.send_message(embed=weather_data, view=view)