import os
import requests
import discord
from discord import app_commands
from typing import Optional

global_instruction = (
    "Provide a detailed and structured response under 2150 characters. "
    "Be concise when possible. Do not use headings (####, ###, ##, #) or bold text (**text**) for structure or emphasis."
)

def perplexity_search(query: str):
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return "PERPLEXITY_API_KEY environment variable not set."
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": global_instruction
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "stream": True,
        "search_domain_filter": "boardgamegeek.com",
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    result = ""
    for line in response.iter_lines():
        if line:
            result += line.decode('utf-8') + "\n"
    return result

def setup(bot):
    bot.tree.add_command(perplexity_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="websearch", description="Search the web using Perplexity AI")
@app_commands.describe(query="Your search query")
async def perplexity_command(interaction: discord.Interaction, query: str):
    thinking_embed = discord.Embed(
        title="🌐 Searching Perplexity...",
        description="Your query is being processed.",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Query", value=query[:1000], inline=False)
    await interaction.response.send_message(embed=thinking_embed)

    result = perplexity_search(query)
    output_embed = discord.Embed(
        title="🔎 Perplexity AI Result",
        color=0x34a853
    )
    output_embed.add_field(name="Query", value=query[:1000], inline=False)
    if result and len(result) > 1024:
        chunks = [result[i:i + 1024] for i in range(0, len(result), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            output_embed.add_field(name=f"Answer (Part {idx})", value=chunk, inline=False)
    else:
        output_embed.add_field(name="Answer", value=result if result else "No response from Perplexity.", inline=False)
    await interaction.edit_original_response(embed=output_embed)
