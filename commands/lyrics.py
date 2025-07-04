import discord
from discord import app_commands
import aiohttp
from commands.utils import cooldown
import os

GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")
GENIUS_API_URL = "https://api.genius.com"

async def search_genius_song(query):
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    params = {"q": query}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GENIUS_API_URL}/search", headers=headers, params=params) as resp:
            data = await resp.json()
            hits = data.get("response", {}).get("hits", [])
            if not hits:
                return None
            song_info = hits[0]["result"]
            return {
                "title": song_info["title"],
                "artist": song_info["primary_artist"]["name"],
                "url": song_info["url"]
            }

async def fetch_lyrics_from_url(url):
    # Genius API does not provide lyrics directly, so we scrape the page
    # This is a simple approach and may break if Genius changes their HTML
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    import re
    from html import unescape
    # Try to extract the lyrics from the page
    m = re.search(r'<div[^>]+data-lyrics-container="true"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        # fallback: try to extract all lyrics containers
        containers = re.findall(r'<div[^>]+data-lyrics-container="true"[^>]*>(.*?)</div>', html, re.DOTALL)
        if not containers:
            return None
        lyrics = "\n".join([re.sub(r'<.*?>', '', c) for c in containers])
    else:
        lyrics = re.sub(r'<.*?>', '', m.group(1))
    return unescape(lyrics).strip()

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="lyrics", description="Find song lyrics from Genius")
@app_commands.describe(
    query="The song you want to search for",
)
@app_commands.checks.dynamic_cooldown(cooldown)
async def lyrics_command(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    song = await search_genius_song(query)
    if not song:
        await interaction.followup.send("Song not found.")
        return
    lyrics = await fetch_lyrics_from_url(song["url"])
    if not lyrics:
        await interaction.followup.send(
            f"Lyrics not found for **{song['title']}** by **{song['artist']}**.\n<{song['url']}>"
        )
        return
    # Discord message limit is 2000 chars
    if len(lyrics) > 1900:
        lyrics = lyrics[:1900] + "...\n[Lyrics truncated]\n" + song["url"]
    embed = discord.Embed(
        title=f"{song['title']} - {song['artist']}",
        description=lyrics,
        url=song["url"],
        color=0x34a853
    )
    await interaction.followup.send(embed=embed)

def setup(bot):
    """
    Register the lyrics command with the bot
    """
    bot.tree.add_command(lyrics_command)
