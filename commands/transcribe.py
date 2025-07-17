import discord
from discord.ext import commands
from discord import Embed
import asyncio
import os
import groq
import logging

logger = logging.getLogger(__name__)

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
        # Don't react to messages from bots
        if message.author.bot:
            logger.debug(f"Ignoring message from bot: {message.author.name}")
            return

        # React only to Discord voice messages
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.startswith("voice-message"):
                    logger.info(f"Found voice message in channel {message.channel.name if hasattr(message.channel, 'name') else 'DM'} from {message.author.name}")
                    try:
                        await message.add_reaction(self.emoji)
                        logger.info(f"Added reaction {self.emoji} to voice message")
                    except Exception as e:
                        logger.error(f"Failed to add reaction to voice message: {e}")
                    break

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User | discord.Member):
        # Log all reactions for debugging
        logger.debug(f"Reaction {reaction.emoji} added by {user.name} (ID: {user.id}) to message {reaction.message.id}")

        # Ignore reactions from bots (including our own)
        if user.bot:
            logger.debug(f"Ignoring reaction from bot user: {user.name}")
            return

        # Only respond to the notebook emoji
        if reaction.emoji != self.emoji:
            logger.debug(f"Ignoring reaction with emoji {reaction.emoji} (not {self.emoji})")
            return

        # Get the message
        message = reaction.message

        # Check if our bot has reacted with the emoji already
        try:
            # Get the specific reaction object for our emoji
            bot_reaction = discord.utils.get(message.reactions, emoji=self.emoji)
            if not bot_reaction:
                logger.debug("Bot reaction not found")
                return

            # Check if bot is in the users who reacted
            users = await bot_reaction.users().flatten()
            bot_user_ids = [u.id for u in users if u.id == self.bot.user.id]

            if not bot_user_ids:
                logger.debug(f"Bot hasn't reacted with {self.emoji} yet")
                return

            logger.info(f"Bot has reacted with {self.emoji} and user {user.name} also reacted")
        except Exception as e:
            logger.error(f"Error checking bot reactions: {e}")
            return

        # Look for voice message attachments
        audio_url = None
        try:
            for attachment in message.attachments:
                logger.debug(f"Checking attachment: {attachment.filename}")

                is_audio = False
                # Check if it's a voice message by filename
                if attachment.filename.startswith("voice-message"):
                    is_audio = True
                    logger.debug("Found voice message by filename")
                # Or check if it's an audio file by content type
                elif hasattr(attachment, 'content_type') and attachment.content_type and "audio" in attachment.content_type:
                    is_audio = True
                    logger.debug(f"Found audio by content type: {attachment.content_type}")

                if is_audio:
                    audio_url = attachment.url
                    logger.info(f"Found audio URL: {audio_url}")
                    break

            if not audio_url:
                logger.warning("No audio attachment found in the message")
                return
        except Exception as e:
            logger.error(f"Error processing attachments: {e}")
            return

        # Transcribe the audio
        try:
            logger.info("Starting transcription...")
            await message.channel.trigger_typing()

            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(None, transcribe_audio, audio_url)

            logger.info(f"Transcription completed: {transcript[:50]}...")

            embed = Embed(
                title="Transcription", 
                description=transcript, 
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Requested by {user.name}")

            await message.channel.send(embed=embed)
            logger.info("Transcription sent successfully")
        except Exception as e:
            logger.error(f"Error during transcription process: {e}")
            await message.channel.send(f"Error during transcription: {str(e)}")

async def setup(bot):
    logger.info("Setting up TranscribeVoice cog")
    try:
        await bot.add_cog(TranscribeVoice(bot))
        logger.info("TranscribeVoice cog has been added successfully")
    except Exception as e:
        logger.error(f"Failed to add TranscribeVoice cog: {e}")
