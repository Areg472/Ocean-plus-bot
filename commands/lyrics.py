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
    await interaction.response.defer()
    try:
        song = genius.search_song(query)
    except Exception as e:
        await interaction.followup.send("An error occurred while searching for lyrics.")
        return

    if not song:
        await interaction.followup.send("No lyrics found for that song.")
        return

    # Discord message limit is 2000 chars
    lyrics = song.lyrics
    url = getattr(song, "url", None)
    if len(lyrics) > 1900:
        short_lyrics = lyrics[:1900] + "...\n[Lyrics truncated]"
        if url:
            short_lyrics += f"\n{url}"
    else:
        short_lyrics = lyrics

    embed = discord.Embed(
        title=f"{song.title} - {song.artist}",
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
