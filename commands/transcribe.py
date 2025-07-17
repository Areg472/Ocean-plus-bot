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
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            url=audio_url,
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
        # Don't react to our own messages
        if message.author.bot:
            return

        # React only to Discord voice messages
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.startswith("voice-message"):
                    await message.add_reaction(self.emoji)
                    break

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User | discord.Member):
        # Ignore reactions from bots (including our own)
        if user.bot:
            return

        # Only respond to the correct emoji
        if reaction.emoji != self.emoji:
            return

        message = reaction.message

        # Check if the bot has already reacted with this emoji
        bot_reacted = False
        for msg_reaction in message.reactions:
            if msg_reaction.emoji == self.emoji:
                users = await msg_reaction.users().flatten()
                if self.bot.user in users:
                    bot_reacted = True
                    break

        if not bot_reacted:
            return
        # Check for audio attachment or voice message
        audio_url = None
        for attachment in reaction.message.attachments:
            if (
                (attachment.content_type and "audio" in attachment.content_type)
                or (attachment.filename.startswith("voice-message"))
            ):
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
