import discord
from discord import app_commands
import asyncio
from commands.utils import cooldown
from lyricsgenius import Genius
import os

GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN", "YOUR_GENIUS_ACCESS_TOKEN_HERE")
if not GENIUS_TOKEN or GENIUS_TOKEN == "YOUR_GENIUS_ACCESS_TOKEN_HERE":
    raise RuntimeError("Genius API access token not set. Set the GENIUS_ACCESS_TOKEN environment variable.")

genius = Genius(GENIUS_TOKEN)

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
        song = await asyncio.to_thread(genius.search_song, query)
    except Exception as e:
        print(f"Error searching for lyrics: {e}")  # For debugging
        await interaction.followup.send("An error occurred while searching for lyrics.")
        return

    if not song:
        await interaction.followup.send("No lyrics found for that song.")
        return

    # Defensive: Check if lyrics, title, and artist exist
    lyrics = getattr(song, "lyrics", None)
    title = getattr(song, "title", "Unknown Title")
    artist = getattr(song, "artist", "Unknown Artist")
    url = getattr(song, "url", None)

    if not lyrics:
        await interaction.followup.send("Lyrics could not be retrieved for this song.")
        return

    if len(lyrics) > 1900:
        short_lyrics = lyrics[:1900] + "...\n[Lyrics truncated]"
        if url:
            short_lyrics += f"\n{url}"
    else:
        short_lyrics = lyrics

    embed = discord.Embed(
        title=f"{title} - {artist}",
        description=short_lyrics,
        url=url if url else discord.Embed.Empty,
        color=0x34a853
    )
    await interaction.followup.send(embed=embed)

def setup(bot):
    """
    Register the lyrics command with the bot
    """
    bot.tree.add_command(lyrics_command)
