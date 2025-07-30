import discord
from discord import app_commands
import os
from mistralai import Mistral

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name='Transcribe Message')
async def transcribe_message(interaction: discord.Interaction, message: discord.Message):
    
    voice_attachments = [
        attachment for attachment in message.attachments 
        if attachment.content_type and (
            'audio' in attachment.content_type or 
            'video' in attachment.content_type or
            attachment.filename.endswith((
                '.mp3', '.wav', '.ogg', '.m4a', '.webm', # audio
                '.mp4', '.mov', '.mkv', '.avi', '.webm'  # video
            ))
        )
    ]
    
    if not voice_attachments:
        await interaction.response.send_message(
            "❌ This message doesn't contain any audio or video attachments to transcribe.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    try:
        voice_attachment = voice_attachments[0]
        
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            await interaction.followup.send(
                "❌ Mistral API key not configured.", 
                ephemeral=True
            )
            return
        
        # Initialize the Mistral client
        client = Mistral(api_key=api_key)
        
        # Get the transcription using file URL
        transcription_response = client.audio.transcriptions.complete(
            model="voxtral-mini-2507",
            file_url=voice_attachment.url
        )
        
        transcription = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
        
        embed = discord.Embed(
            title="🎤 Voice Message Transcription",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Original Message", 
            value=f"[Jump to message]({message.jump_url})", 
            inline=False
        )
        embed.add_field(
            name="Transcription", 
            value=transcription, 
            inline=False
        )
        embed.set_footer(text="Transcribed by Mistral AI")
        
        await interaction.followup.send(embed=embed)
                    
    except Exception as e:
        await interaction.followup.send(
            f"❌ An error occurred during transcription: {str(e)}", 
            ephemeral=True
        )

def setup(bot):
    bot.tree.add_command(transcribe_message)