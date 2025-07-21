import discord
import aiohttp
import os
import tempfile
from discord.ext import commands

# Store voice messages that have been reacted to
voice_messages = {}

async def download_audio(url: str) -> str:
    """Download audio file to temporary location"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
                temp_file.write(await response.read())
                temp_file.close()
                return temp_file.name
    return None

async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Mistral API"""
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        return "Error: Mistral API key not configured"
    
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as audio_file:
                data = aiohttp.FormData()
                data.add_field('file', audio_file, filename='audio.ogg')
                data.add_field('model', 'voxtral-mini-2507')
                
                headers = {'x-api-key': api_key}
                
                async with session.post(
                    'https://api.mistral.ai/v1/audio/transcriptions',
                    headers=headers,
                    data=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('text', 'No transcription available')
                    else:
                        return f"Error: API returned status {response.status}"
    except Exception as e:
        return f"Error during transcription: {str(e)}"
    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except:
            pass

class TranscribeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """React to voice messages with transcribe emoji"""
        if message.author.bot:
            return
        
        print(f"Checking message from {message.author}: {len(message.attachments)} attachments")
        
        # Check if message has voice attachments
        for attachment in message.attachments:
            print(f"Attachment: {attachment.filename}, Content-Type: {attachment.content_type}")
            if attachment.content_type and 'audio' in attachment.content_type:
                print(f"Found voice message! Adding reaction...")
                # React with transcribe emoji
                await message.add_reaction('📝')
                # Store the message for potential transcription
                voice_messages[message.id] = {
                    'url': attachment.url,
                    'message': message,
                    'transcribed': False
                }
                print(f"Stored voice message with ID: {message.id}")
                break

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """Handle transcription requests when users react with 📝"""
        if user.bot:
            return
        
        print(f"Reaction added: {reaction.emoji} by {user.display_name} on message {reaction.message.id}")
        print(f"Voice messages stored: {list(voice_messages.keys())}")
        
        # Check if it's the transcribe emoji and the message is a voice message
        if str(reaction.emoji) == '📝' and reaction.message.id in voice_messages:
            voice_data = voice_messages[reaction.message.id]
            
            print(f"Found voice message! Transcribed: {voice_data['transcribed']}")
            
            # Skip if already transcribed
            if voice_data['transcribed']:
                print("Already transcribed, skipping...")
                return
            
            # Check if user is not the original message author (to avoid self-transcription)
            if user.id != voice_data['message'].author.id:
                voice_data['transcribed'] = True
                print(f"Starting transcription for user {user.display_name}")
                
                # Send "transcribing..." message
                transcribing_msg = await reaction.message.reply("🔄 Transcribing voice message...")
                
                try:
                    # Download and transcribe the audio
                    temp_file = await download_audio(voice_data['url'])
                    if temp_file:
                        transcription = await transcribe_audio(temp_file)
                        
                        # Create embed for transcription
                        embed = discord.Embed(
                            title="🎤 Voice Message Transcription",
                            description=transcription,
                            color=0x5865F2
                        )
                        embed.set_footer(
                            text=f"Original message by {voice_data['message'].author.display_name} • Requested by {user.display_name}",
                            icon_url=voice_data['message'].author.display_avatar.url
                        )
                        
                        # Edit the transcribing message with the result
                        await transcribing_msg.edit(content="", embed=embed)
                    else:
                        await transcribing_msg.edit(content="❌ Failed to download audio file")
                        
                except Exception as e:
                    print(f"Error during transcription: {e}")
                    await transcribing_msg.edit(content=f"❌ Error during transcription: {str(e)}")
            else:
                print("User is the original author, skipping self-transcription")

def setup(bot):
    """Setup the transcribe functionality"""
    bot.add_cog(TranscribeCog(bot))
    print("Transcribe cog added successfully!")
