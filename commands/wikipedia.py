import discord
from discord import app_commands
import wikipediaapi
from commands.utils import cooldown

def setup(bot):
    bot.tree.add_command(wiki_search_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="wikipedia", description="Search wikipedia articles")
@app_commands.describe(query="The search query")
@app_commands.checks.dynamic_cooldown(cooldown)
async def wiki_search_command(interaction: discord.Interaction, query: str):
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