import discord
from discord import app_commands
import asyncio
from commands.utils import cooldown
import aiohttp
import os
from bs4 import BeautifulSoup

GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN", "YOUR_GENIUS_ACCESS_TOKEN_HERE")
if not GENIUS_TOKEN or GENIUS_TOKEN == "YOUR_GENIUS_ACCESS_TOKEN_HERE":
    raise RuntimeError("Genius API access token not set. Set the GENIUS_ACCESS_TOKEN environment variable.")

GENIUS_API_URL = "https://api.genius.com"
GENIUS_HEADERS = {
    "Authorization": f"Bearer {GENIUS_TOKEN}",
    "User-Agent": "Mozilla/5.0 (compatible; DiscordBot/1.0; +https://github.com/Areg472/Ocean-plus-bot)"
}

async def fetch_song_data(query):
    async with aiohttp.ClientSession() as session:
        params = {"q": query}
        async with session.get(f"{GENIUS_API_URL}/search", headers=GENIUS_HEADERS, params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Genius API returned status {resp.status}")
            data = await resp.json()
            hits = data["response"]["hits"]
            if not hits:
                return None
            # Take the first result
            song_info = hits[0]["result"]
            return {
                "title": song_info["title"],
                "artist": song_info["primary_artist"]["name"],
                "url": song_info["url"]
            }

async def fetch_lyrics(song_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(song_url, headers={"User-Agent": GENIUS_HEADERS["User-Agent"]}) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            # Genius lyrics are in <div data-lyrics-container="true">
            lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
            lyrics = "\n".join(div.get_text(separator="\n") for div in lyrics_divs)
            return lyrics.strip() if lyrics else None

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="lyrics", description="Find song lyrics from Genius")
@app_commands.describe(
    query="The song you want to search for",
)
@app_commands.checks.dynamic_cooldown(cooldown)
async def lyrics_command(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    try:
        song_data = await fetch_song_data(query)
    except Exception as e:
        print(f"Error searching for lyrics: {e}")
        await interaction.followup.send("An error occurred while searching for lyrics.")
        return

    if not song_data:
        await interaction.followup.send("No lyrics found for that song.")
        return

    lyrics = await fetch_lyrics(song_data["url"])
    if not lyrics:
        await interaction.followup.send("Lyrics could not be retrieved for this song.")
        return

    if len(lyrics) > 1900:
        short_lyrics = lyrics[:1900] + "...\n[Lyrics truncated]\n" + song_data["url"]
    else:
        short_lyrics = lyrics

    embed = discord.Embed(
        title=f"{song_data['title']} - {song_data['artist']}",
        description=short_lyrics,
        url=song_data["url"],
        color=0x34a853
    )
    await interaction.followup.send(embed=embed)

def setup(bot):
    """
    Register the lyrics command with the bot
    """
    bot.tree.add_command(lyrics_command)
