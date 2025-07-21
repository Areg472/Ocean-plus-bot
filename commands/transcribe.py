import discord
from discord import app_commands
import aiohttp
import os

@app_commands.context_menu(name='Transcribe Voice Message')
async def transcribe_message(interaction: discord.Interaction, message: discord.Message):
    """Transcribe a voice message using Mistral API"""
    
    # Check if message has voice attachments
    voice_attachments = [
        attachment for attachment in message.attachments 
        if attachment.content_type and (
            'audio' in attachment.content_type or 
            attachment.filename.endswith(('.mp3', '.wav', '.ogg', '.m4a', '.webm'))
        )
    ]
    
    if not voice_attachments:
        await interaction.response.send_message(
            "❌ This message doesn't contain any voice attachments to transcribe.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    try:
        # Get the first voice attachment
        voice_attachment = voice_attachments[0]
        
        # Prepare API request
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            await interaction.followup.send(
                "❌ Mistral API key not configured.", 
                ephemeral=True
            )
            return
        
        headers = {
            'x-api-key': api_key
        }
        
        # Prepare form data with file_url as multipart
        form_data = aiohttp.FormData()
        form_data.add_field('file_url', voice_attachment.url)
        form_data.add_field('model', 'voxtral-mini-2507')
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.mistral.ai/v1/audio/transcriptions',
                headers=headers,
                data=form_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    transcription = result.get('text', 'No transcription available')
                    
                    # Create embed
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
                    
                else:
                    error_text = await response.text()
                    await interaction.followup.send(
                        f"❌ Transcription failed: {response.status} - {error_text}", 
                        ephemeral=True
                    )
    except Exception as e:
        await interaction.followup.send(
            f"❌ An error occurred during transcription: {str(e)}", 
            ephemeral=True
        )

def setup(bot):
    """Register the transcribe command with the bot"""
    bot.tree.add_command(transcribe_message)
