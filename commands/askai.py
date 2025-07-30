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
    print("[ASKAI] Command added to tree")

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
    
    print(f"[ASKAI] Creating modal for attachment: {voice_attachments[0].filename}")
    # Create modal for user input
    modal = AskAIModal(voice_attachments[0])  # Use first valid attachment
    await interaction.response.send_modal(modal)
    print("[ASKAI] Modal sent to user")

class AskAIModal(discord.ui.Modal, title="Ask AI about this recording"):
    def __init__(self, attachment):
        super().__init__()
        self.attachment = attachment
        print(f"[ASKAI] Modal initialized for file: {attachment.filename}")
    
    question = discord.ui.TextInput(
        label="What would you like to ask about this recording?",
        placeholder="e.g., What's being discussed in this audio?",
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        print(f"[ASKAI] Modal submitted with question: {self.question.value[:100]}...")
        print(f"[ASKAI] Processing file: {self.attachment.filename}")
        print(f"[ASKAI] File URL: {self.attachment.url}")
        
        thinking_embed = discord.Embed(
            title="🤔 Transcribing recording...",
            description="First transcribing the audio, then analyzing with AI...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="File", value=self.attachment.filename, inline=False)
        thinking_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
        
        print("[ASKAI] Sending thinking embed")
        await interaction.response.send_message(embed=thinking_embed)
        print("[ASKAI] Thinking embed sent")
        
        try:
            print("[ASKAI] Starting transcription...")
            # Step 1: Transcribe using same method as transcribe.py
            transcription_response = client.audio.transcriptions.complete(
                model="voxtral-mini-2507",
                file_url=self.attachment.url
            )
            print(f"[ASKAI] Transcription response received: {type(transcription_response)}")
            
            # Extract transcription text using same method as transcribe.py
            transcription_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
            print(f"[ASKAI] Transcription text length: {len(transcription_text)}")
            print(f"[ASKAI] Transcription preview: {transcription_text[:100]}...")
            
            # Update embed to show transcription is done
            analysis_embed = discord.Embed(
                title="🤔 Analyzing transcription...",
                description="Transcription complete! Now analyzing with AI...",
                color=0x4285f4
            )
            analysis_embed.add_field(name="File", value=self.attachment.filename, inline=False)
            analysis_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
            
            print("[ASKAI] Updating embed to show analysis stage")
            await interaction.edit_original_response(embed=analysis_embed)
            print("[ASKAI] Analysis embed sent")
            
            # Step 2: Send transcription + question to AI
            combined_prompt = f"Here is a transcription of an audio/video file:\n\n{transcription_text}\n\nQuestion: {self.question.value}"
            print(f"[ASKAI] Combined prompt length: {len(combined_prompt)}")
            print(f"[ASKAI] Calling get_ai_response...")
            
            answer = await get_ai_response(combined_prompt, user_id=interaction.user.id, model="mistral-small-2506")
            print(f"[ASKAI] AI response received, length: {len(answer)}")
            print(f"[ASKAI] AI response preview: {answer[:100]}...")
            
        except Exception as error:
            print(f"[ASKAI] Error occurred: {str(error)}")
            print(f"[ASKAI] Error type: {type(error)}")
            import traceback
            print(f"[ASKAI] Traceback: {traceback.format_exc()}")
            answer = f"An error occurred while processing the recording: {str(error)}"
        
        print("[ASKAI] Creating final response embed")
        # Create response embed
        response_embed = discord.Embed(title="🎤 AI Analysis", color=0x34a853)
        response_embed.add_field(name="File", value=self.attachment.filename, inline=False)
        response_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
        
        # Handle long responses
        if len(answer) > 1024:
            print(f"[ASKAI] Answer is long ({len(answer)} chars), chunking...")
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
        else:
            print(f"[ASKAI] Answer fits in one field ({len(answer)} chars)")
            response_embed.add_field(name="Answer", value=answer, inline=False)
        
        try:
            print("[ASKAI] Attempting to edit original response")
            await interaction.edit_original_response(embed=response_embed)
            print("[ASKAI] Successfully edited original response")
        except Exception as edit_error:
            print(f"[ASKAI] Error editing response: {str(edit_error)}")
            try:
                print("[ASKAI] Attempting followup send")
                await interaction.followup.send(embed=response_embed)
                print("[ASKAI] Successfully sent followup")
            except Exception as followup_error:
                print(f"[ASKAI] Error sending followup: {str(followup_error)}")
