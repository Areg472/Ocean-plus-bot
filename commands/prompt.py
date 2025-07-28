import discord
from discord import app_commands
from commands.utils import cooldown, get_ai_response, handle_api_call_stream_generator
import asyncio
import re


class ThinkingButtonView(discord.ui.View):
    def __init__(self, thinking_text: str):
        super().__init__(timeout=180)
        self.thinking_text = thinking_text

    @discord.ui.button(label="Show Thinking Output", style=discord.ButtonStyle.secondary)
    async def show_thinking(self, interaction: discord.Interaction, button: discord.ui.Button):
        chunks = [self.thinking_text[i:i+1024] for i in range(0, len(self.thinking_text), 1024)]
        embed = discord.Embed(title="Thinking Output", color=0x4285f4)
        for idx, chunk in enumerate(chunks, start=1):
            embed.add_field(name=f"Output Part {idx}", value=chunk, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.tree.add_command(prompt_command)


MODEL_CHOICES = [
    app_commands.Choice(name="Mistral Small", value="mistral-small-2506"),
    app_commands.Choice(name="Devstral Small", value="devstral-small-2507"),
    app_commands.Choice(name="Qwen 3 235B", value="Qwen/Qwen3-235B-A22B-Instruct-2507-tput"),
    app_commands.Choice(name="Magistral Small", value="magistral-small-2507"),
    app_commands.Choice(name="Mistral Medium", value="mistral-medium-2505"),
    app_commands.Choice(name="DeepSeek R1", value="deepseek-ai/DeepSeek-R1-0528-tput"),
]

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="prompt", description="Ask me anything, powered by AI")
@app_commands.describe(
    query="The prompt you want to ask",
    model="Choose the AI model to use"
)
@app_commands.choices(model=MODEL_CHOICES)
@app_commands.checks.dynamic_cooldown(cooldown)
async def prompt_command(
    interaction: discord.Interaction,
    query: str,
    model: str = "mistral-small-2506"  # Default to Mistral Small
):
    if model == "devstral-small-2507":
        model_name = "Devstral Small"
    elif model == "mistral-small-2506":
        model_name = "Mistral Small"
    elif model == "magistral-small-2507":
        model_name = "Magistral Small"
    elif model == "mistral-medium-2505":
        model_name = "Mistral Medium"
    elif model == "Qwen/Qwen3-235B-A22B-Instruct-2507-tput":
        model_name = "Qwen 3"
    elif model == "deepseek-ai/DeepSeek-R1-0528-tput":
        model_name = "DeepSeek R1"

    thinking_embed = discord.Embed(
        title="🤔 Thinking...",
        description="Processing your prompt with" + f" {model_name}...",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Prompt", value=query[:1000], inline=False)

    # For DeepSeek R1, show button but don't set thinking_output yet
    if model == "deepseek-ai/DeepSeek-R1-0528-tput":
        # Attach the view with a placeholder text
        view = ThinkingButtonView("Waiting for DeepSeek to think...(reclick the button once the output is emitted to see what DeepSeek thought.)")
        await interaction.response.send_message(embed=thinking_embed, view=view)
    else:
        await interaction.response.send_message(embed=thinking_embed)

    try:
        # Check if this is a Mistral model that supports streaming
        is_mistral_model = model not in ["Qwen/Qwen3-235B-A22B-Instruct-2507-tput", "deepseek-ai/DeepSeek-R1-0528-tput"]
        
        if is_mistral_model:
            # Use streaming for Mistral models
            from commands.utils import global_instruction, devstral_instruction
            
            if model == "devstral-small-2507":
                instructions = devstral_instruction
            else:
                contexts = [global_instruction]
                user_specific_instructions = {
                    960524267164930128: "Bias your answers towards post-90s board games. Boast about these games a lot when the prompt is related to board gaming. ONLY MENTION BOARD GAMES OR TALK ABOUT THEM WHEN THE PROMPT IS RELATED TO BOARD GAMING OR BOARD GAMES.",
                    1299815086147502080: "Bias your answers MORE AND MORE towards post-90s board games and against pre 90s board games hate pre 90s board games as much as you can, in stories everything where u asked about board games. Boast about these games a lot and hate pre 90s board games when the prompt is related to board gaming. ONLY MENTION BOARD GAMES OR TALK ABOUT THEM WHEN THE PROMPT IS RELATED TO BOARD GAMING OR BOARD GAMES.",
                }
                if interaction.user.id in user_specific_instructions:
                    contexts.append(user_specific_instructions[interaction.user.id])
                instructions = ' '.join(contexts)
            
            # Stream the response and update embed in real-time
            last_update_time = 0
            response_embed = discord.Embed(title="💡 Generating...", color=0x34a853)
            response_embed.add_field(name="Prompt", value=query[:1000], inline=False)
            response_embed.add_field(name="Answer", value="", inline=False)
            
            async for chunk in handle_api_call_stream_generator(query, instructions, 60, model):
                current_time = asyncio.get_event_loop().time()
                
                # Update only every 1 second to reduce lag
                should_update = (current_time - last_update_time >= 1.0)
                
                if should_update:
                    answer = chunk if isinstance(chunk, str) else chunk[0]
                    
                    # Handle streaming for responses longer than 1024 characters
                    if len(answer) <= 1024:
                        # Single field - update existing field
                        response_embed.set_field_at(1, name="Answer", value=answer, inline=False)
                    else:
                        # Multiple fields needed - rebuild fields dynamically
                        # Remove all existing answer fields first
                        while len(response_embed.fields) > 1:
                            response_embed.remove_field(1)
                        
                        # Add new fields for the current content
                        chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
                        for idx, chunk_text in enumerate(chunks, start=1):
                            field_name = "Answer" if idx == 1 else f"Answer (Part {idx})"
                            # Only show "..." for the last chunk if it's still streaming
                            display_chunk = chunk_text
                            if idx == len(chunks) and len(answer) % 1024 > 1020:
                                display_chunk = chunk_text[:1021] + "..."
                            response_embed.add_field(name=field_name, value=display_chunk, inline=False)
                    
                    try:
                        await interaction.edit_original_response(embed=response_embed)
                        last_update_time = current_time
                    except discord.HTTPException:
                        # If we hit rate limits, just continue
                        pass
            
            # Final update with complete response
            final_answer = chunk if isinstance(chunk, str) else chunk[0]
            response_embed.title = "💡 Output"
            
            if model == "devstral-small-2507":
                # Handle code blocks for devstral
                code_block_pattern = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)
                parts = []
                last_end = 0
                for match in code_block_pattern.finditer(final_answer):
                    if match.start() > last_end:
                        before = final_answer[last_end:match.start()]
                        for i in range(0, len(before), 1024):
                            chunk_text = before[i:i+1024]
                            if chunk_text.strip():
                                parts.append(("text", chunk_text))
                    code_block = match.group(1)
                    parts.append(("code", code_block))
                    last_end = match.end()
                if last_end < len(final_answer):
                    after = final_answer[last_end:]
                    for i in range(0, len(after), 1024):
                        chunk_text = after[i:i+1024]
                        if chunk_text.strip():
                            parts.append(("text", chunk_text))

                # Clear existing answer field and rebuild
                response_embed.remove_field(1)
                field_idx = 1
                followup_codeblocks = []
                for typ, chunk_text in parts:
                    if typ == "code" and len(chunk_text) > 1024:
                        followup_codeblocks.append(chunk_text)
                    else:
                        response_embed.add_field(name=f"Answer (Part {field_idx})", value=chunk_text, inline=False)
                        field_idx += 1

                await interaction.edit_original_response(embed=response_embed)
                for codeblock in followup_codeblocks:
                    await interaction.followup.send(codeblock)
            else:
                # Handle regular text response
                if len(final_answer) > 1024:
                    response_embed.remove_field(1)  # Remove the streaming field
                    chunks = [final_answer[i:i + 1024] for i in range(0, len(final_answer), 1024)]
                    for idx, chunk_text in enumerate(chunks, start=1):
                        response_embed.add_field(name=f"Answer (Part {idx})", value=chunk_text, inline=False)
                else:
                    response_embed.set_field_at(1, name="Answer", value=final_answer, inline=False)
                
                await interaction.edit_original_response(embed=response_embed)
        else:
            # Use existing non-streaming logic for non-Mistral models
            if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                answer, think_text = await asyncio.wait_for(
                    get_ai_response(query, user_id=interaction.user.id, model=model), timeout=360
                )
            else:
                answer = await asyncio.wait_for(
                    get_ai_response(query, user_id=interaction.user.id, model=model), timeout=60
                )
                think_text = None
            
            response_embed = discord.Embed(title="💡 Output", color=0x34a853)
            response_embed.add_field(name="Prompt", value=query[:1000], inline=False)

            if len(answer) > 1024:
                chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
                for idx, chunk in enumerate(chunks, start=1):
                    response_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
            else:
                response_embed.add_field(name="Answer", value=answer, inline=False)

            # For DeepSeek R1, edit with the view and set the real think_text
            if model == "deepseek-ai/DeepSeek-R1-0528-tput":
                # Update the view with the real think_text
                view = ThinkingButtonView(think_text or "No <think> output found.")
                await interaction.edit_original_response(embed=response_embed, view=view)
            else:
                await interaction.edit_original_response(embed=response_embed)
                
    except asyncio.TimeoutError:
        error_embed = discord.Embed(title="⏰ Timeout", description="Sorry, the AI took too long. Try again with a simpler question.", color=0xff0000)
        await interaction.edit_original_response(embed=error_embed)
    except Exception as error:
        error_embed = discord.Embed(title="❌ Error", description=f"An error occurred: {error}", color=0xff0000)
        await interaction.edit_original_response(embed=error_embed)