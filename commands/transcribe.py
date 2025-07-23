import discord
from discord import app_commands
import aiohttp
import os

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name='Transcribe Voice Message')
async def transcribe_message(interaction: discord.Interaction, message: discord.Message):
    
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
        voice_attachment = voice_attachments[0]
        
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
        
        async with aiohttp.ClientSession() as session:
            async with session.get(voice_attachment.url) as audio_response:
                if audio_response.status != 200:
                    await interaction.followup.send(
                        "❌ Failed to download audio file.", 
                        ephemeral=True
                    )
                    return
                
                audio_data = await audio_response.read()
        
        form_data = aiohttp.FormData()
        form_data.add_field('file', audio_data, filename=voice_attachment.filename, content_type=voice_attachment.content_type or 'audio/ogg')
        form_data.add_field('model', 'voxtral-mini-2507')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.mistral.ai/v1/audio/transcriptions',
                headers=headers,
                data=form_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    transcription = result.get('text', 'No transcription available')
                    
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
    bot.tree.add_command(transcribe_message)
