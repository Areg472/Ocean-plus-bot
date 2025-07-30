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
    bot.tree.add_command(askai_context)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.context_menu(name="Ask AI")
async def askai_context(interaction: discord.Interaction, message: discord.Message):
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
    
    if not voice_attachments:
        await interaction.response.send_message(
            "❌ This command only works on messages with voice or video recordings.", 
            ephemeral=True
        )
        return
    
    # Create modal for user input
    modal = AskAIModal(voice_attachments[0])  # Use first valid attachment
    await interaction.response.send_modal(modal)

class AskAIModal(discord.ui.Modal, title="Ask AI about this recording"):
    def __init__(self, attachment):
        super().__init__()
        self.attachment = attachment
    
    question = discord.ui.TextInput(
        label="What would you like to ask about this recording?",
        placeholder="e.g., What's being discussed in this audio?",
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        thinking_embed = discord.Embed(
            title="🤔 Transcribing recording...",
            description="First transcribing the audio, then analyzing with AI...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="File", value=self.attachment.filename, inline=False)
        thinking_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
        
        await interaction.response.send_message(embed=thinking_embed)
        
        try:
            # Step 1: Transcribe using same method as transcribe.py
            transcription_response = client.audio.transcriptions.complete(
                model="voxtral-mini-2507",
                file_url=self.attachment.url
            )
            
            # Extract transcription text using same method as transcribe.py
            transcription_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
            
            # Update embed to show transcription is done
            analysis_embed = discord.Embed(
                title="🤔 Analyzing transcription...",
                description="Transcription complete! Now analyzing with AI...",
                color=0x4285f4
            )
            analysis_embed.add_field(name="File", value=self.attachment.filename, inline=False)
            analysis_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
            
            await interaction.edit_original_response(embed=analysis_embed)
            
            # Step 2: Send transcription + question to AI
            combined_prompt = f"Here is a transcription of an audio/video file:\n\n{transcription_text}\n\nQuestion: {self.question.value}"
            
            answer = await get_ai_response(combined_prompt, user_id=interaction.user.id, model="mistral-small-2506")
            
        except Exception as error:
            print(f"Error in askai: {str(error)}")
            answer = f"An error occurred while processing the recording: {str(error)}"
        
        # Create response embed
        response_embed = discord.Embed(title="🎤 AI Analysis", color=0x34a853)
        response_embed.add_field(name="File", value=self.attachment.filename, inline=False)
        response_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
        
        # Handle long responses
        if len(answer) > 1024:
            chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
            for idx, chunk in enumerate(chunks, start=1):
                response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
        else:
            response_embed.add_field(name="Answer", value=answer, inline=False)
        
        try:
            await interaction.edit_original_response(embed=response_embed)
        except Exception as edit_error:
            print(f"Error editing response: {str(edit_error)}")
            try:
                await interaction.followup.send(embed=response_embed)
            except Exception as followup_error:
                print(f"Error sending followup: {str(followup_error)}")
            print(f"Error editing response: {str(edit_error)}")
            try:
                await interaction.followup.send(embed=response_embed)
            except Exception as followup_error:
                print(f"Error sending followup: {str(followup_error)}")
