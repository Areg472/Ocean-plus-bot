import discord
from discord.ext import commands
from discord import Embed
import asyncio
import os
import groq

def transcribe_audio(audio_url: str) -> str:
    """
    Transcribe audio using Groq Whisper-large-v3-turbo API via groq library, sending the file link.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return "[Groq API key not set]"

    try:
        client = groq.Groq(api_key=groq_api_key)
        # Use file_url (not url)
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file_url=audio_url,
            response_format="text"
        )
        return transcript
    except Exception as e:
        return f"[Transcription failed: {e}]"

class TranscribeVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "📒"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if the message contains a voice attachment
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and "audio" in attachment.content_type:
                    # React with the notebook emoji
                    await message.add_reaction(self.emoji)
                    break

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User | discord.Member):
        # Only respond to the correct emoji and if the bot was the first to react
        if reaction.emoji != self.emoji:
            return
        message = reaction.message
        # Check if the bot was the first to react
        if not any(r.user_id == self.bot.user.id for r in await message.reactions[0].users().flatten()):
            return
        # Only transcribe if a user (not the bot) clicks the reaction
        if user.id == self.bot.user.id:
            return
        # Check for audio attachment
        audio_url = None
        for attachment in reaction.message.attachments:
            if attachment.content_type and "audio" in attachment.content_type:
                audio_url = attachment.url
                break
        if not audio_url:
            return
        # Transcribe
        await reaction.message.channel.trigger_typing()
        loop = asyncio.get_event_loop()
        transcript = await loop.run_in_executor(None, transcribe_audio, audio_url)
        embed = Embed(title="Transcription", description=transcript, color=discord.Color.blue())
        await reaction.message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TranscribeVoice(bot))
