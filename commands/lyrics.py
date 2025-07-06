import discord
from discord import app_commands
import aiohttp
from commands.utils import cooldown
import lyricsgenius

genius = lyricsgenius.Genius()

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="lyrics", description="Find song lyrics from Genius")
@app_commands.describe(
    query="The song you want to search for",
)
@app_commands.checks.dynamic_cooldown(cooldown)
async def lyrics_command(interaction: discord.Interaction, query: str):
    song = genius.search_song(query)

    # Discord message limit is 2000 chars
    if len(song.lyrics) > 1900:
        short_lyrics = song.lyrics[:1900] + "...\n[Lyrics truncated]\n" + song["url"]
    embed = discord.Embed(
        title=f"{song['title']} - {song['artist']}",
        description=short_lyrics,
        url=song["url"],
        color=0x34a853
    )
    await interaction.followup.send(embed=embed)

def setup(bot):
    """
    Register the lyrics command with the bot
    """
    bot.tree.add_command(lyrics_command)
