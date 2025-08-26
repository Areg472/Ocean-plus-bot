import os
import discord
from discord import app_commands
from discord.ext import commands
from mistralai import Mistral
import asyncio
from commands.utils import get_ai_response

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("Mistral API key is not set in the environment variables.")
client = Mistral(api_key=api_key)

def setup(bot):
    bot.tree.add_command(askai_context)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name="Ask AI (Audio only)")
async def askai_context(interaction: discord.Interaction, message: discord.Message):
    voice_attachments = [
        attachment for attachment in message.attachments 
        if attachment.content_type and (
            'audio' in attachment.content_type or 
            'video' in attachment.content_type or
            attachment.filename.endswith((
                '.mp3', '.wav', '.ogg', '.m4a', '.webm'
            ))
        )
    ]
    
    if not voice_attachments:
        await interaction.response.send_message(
            "❌ This command only works on messages with voice or video recordings.", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    try:
        voice_attachment = voice_attachments[0]
        
        transcription_response = client.audio.transcriptions.complete(
            model="voxtral-mini-2507",
            file_url=voice_attachment.url
        )
        
        transcription_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
        
        answer = await asyncio.wait_for(
            get_ai_response(transcription_text, user_id=interaction.user.id, model="mistral-small-2506"), 
            timeout=60
        )
        
    except asyncio.TimeoutError:
        answer = "Sorry, the AI took too long. Try again with a shorter recording."
    except Exception as error:
        import traceback
        answer = f"An error occurred while processing the recording: {str(error)}"
    
    response_embed = discord.Embed(title="💡 AI Voice Prompt Output", color=0x34a853)
    response_embed.add_field(
        name="Original Message", 
        value=f"[Jump to message]({message.jump_url})", 
        inline=False
    )
    
    if len(answer) > 1024:
        chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
    else:
        response_embed.add_field(name="Answer", value=answer, inline=False)
    
    await interaction.followup.send(embed=response_embed)
