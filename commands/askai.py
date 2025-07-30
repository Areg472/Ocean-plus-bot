import os
import discord
from discord import app_commands
from discord.ext import commands
from mistralai import Mistral
import asyncio

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
    # Check if message has voice/video attachments
    valid_attachments = []
    for attachment in message.attachments:
        # Check for audio and video file extensions
        if attachment.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.mp4', '.avi', '.mov', '.mkv', '.webm')):
            valid_attachments.append(attachment)
    
    if not valid_attachments:
        await interaction.response.send_message(
            "❌ This command only works on messages with voice or video recordings.", 
            ephemeral=True
        )
        return
    
    # Create modal for user input
    modal = AskAIModal(valid_attachments[0])  # Use first valid attachment
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
            title="🤔 Analyzing recording...",
            description="Processing your audio/video with Voxtral AI...",
            color=0x4285f4
        )
        thinking_embed.add_field(name="File", value=self.attachment.filename, inline=False)
        thinking_embed.add_field(name="Question", value=self.question.value[:1000], inline=False)
        
        await interaction.response.send_message(embed=thinking_embed)
        
        try:
            # Process the audio/video with Mistral Voxtral
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": self.attachment.url,
                        },
                        {
                            "type": "text",
                            "text": self.question.value
                        }
                    ]
                }
            ]
            
            def sync_mistral_call():
                return client.chat.complete(
                    model="voxtral-mini-2507",
                    messages=messages
                )
            
            # Make API call in thread to avoid blocking
            chat_response = await asyncio.to_thread(sync_mistral_call)
            answer = chat_response.choices[0].message.content
            
        except asyncio.TimeoutError:
            answer = "Sorry, the AI took too long to process the recording. Try again with a shorter file."
        except Exception as error:
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
        
        await interaction.edit_original_response(embed=response_embed)
