import os
import discord
from discord import app_commands
from discord.ext import commands
from mistralai import Mistral
import asyncio
from commands.utils import get_ai_response

# Initialize Mistral client
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("Mistral API key is not set in the environment variables.")
client = Mistral(api_key=api_key)

def setup(bot):
    print("[ASKAI] Setting up askai command")
    bot.tree.add_command(askai_context)
    print("[ASKAI] Commands added to tree")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name="Ask AI")
async def askai_context(interaction: discord.Interaction, message: discord.Message):
    print(f"[ASKAI] Context menu triggered by user {interaction.user.id}")
    print(f"[ASKAI] Message has {len(message.attachments)} attachments")
    
    # Check if message has voice/video attachments using same logic as transcribe.py
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
    
    print(f"[ASKAI] Found {len(voice_attachments)} valid voice/video attachments")
    
    if not voice_attachments:
        print("[ASKAI] No valid attachments, sending error message")
        await interaction.response.send_message(
            "❌ This command only works on messages with voice or video recordings.", 
            ephemeral=True
        )
        return
    
    # Use defer like transcribe.py does
    print("[ASKAI] Deferring response")
    await interaction.response.defer()
    
    try:
        voice_attachment = voice_attachments[0]
        print(f"[ASKAI] Processing file: {voice_attachment.filename}")
        print(f"[ASKAI] File URL: {voice_attachment.url}")
        
        print("[ASKAI] Starting transcription...")
        # Step 1: Transcribe using same method as transcribe.py
        transcription_response = client.audio.transcriptions.complete(
            model="voxtral-mini-2507",
            file_url=voice_attachment.url
        )
        print(f"[ASKAI] Transcription response received: {type(transcription_response)}")
        
        # Extract transcription text using same method as transcribe.py
        transcription_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
        print(f"[ASKAI] Transcription text length: {len(transcription_text)}")
        print(f"[ASKAI] Transcription preview: {transcription_text[:100]}...")
        
        # Step 2: Send transcription to AI with a default question
        combined_prompt = f"Here is a transcription of an audio/video file:\n\n{transcription_text}\n\nPlease summarize what was discussed in this recording and provide any key insights."
        print(f"[ASKAI] Combined prompt length: {len(combined_prompt)}")
        print(f"[ASKAI] Calling get_ai_response...")
        
        answer = await get_ai_response(combined_prompt, user_id=interaction.user.id, model="mistral-small-2506")
        print(f"[ASKAI] AI response received, length: {len(answer)}")
        print(f"[ASKAI] AI response preview: {answer[:100]}...")
        
        # Create response embed
        embed = discord.Embed(
            title="🎤 AI Analysis of Recording",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Original Message", 
            value=f"[Jump to message]({message.jump_url})", 
            inline=False
        )
        embed.add_field(
            name="File", 
            value=voice_attachment.filename, 
            inline=False
        )
        
        # Handle long responses
        if len(answer) > 1024:
            print(f"[ASKAI] Answer is long ({len(answer)} chars), chunking...")
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                embed.add_field(name=f"Analysis (Part {idx})", value=chunk, inline=False)
        else:
            print(f"[ASKAI] Answer fits in one field ({len(answer)} chars)")
            embed.add_field(name="Analysis", value=answer, inline=False)
        
        embed.set_footer(text="Analyzed by Mistral AI")
        
        print("[ASKAI] Sending followup with embed")
        await interaction.followup.send(embed=embed)
        print("[ASKAI] Successfully sent response")
        
    except Exception as error:
        print(f"[ASKAI] Error occurred: {str(error)}")
        print(f"[ASKAI] Error type: {type(error)}")
        import traceback
        print(f"[ASKAI] Traceback: {traceback.format_exc()}")
        await interaction.followup.send(
            f"❌ An error occurred while processing the recording: {str(error)}", 
            ephemeral=True
        )
