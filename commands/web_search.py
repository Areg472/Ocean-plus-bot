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
    print(f"[Perplexity] Query: {query}")
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("[Perplexity] Error: API key not set")
        return "PERPLEXITY_API_KEY environment variable not set.", None
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
        "enable_search_classifier": True,
        "stream": False,
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"[Perplexity] API status: {response.status_code}")
    if response.status_code != 200:
        print(f"[Perplexity] API error: {response.text}")
        return f"Error: {response.status_code} - {response.text}", None
    data = response.json()
    try:
        print(data)
        result = data["choices"][0]["message"]["content"]
        print(f"[Perplexity] Result: {result[:200]}...")  # Print first 200 chars
        # Citations are in data["citations"], which is a list of URLs
        citations = data.get("citations", None)
    except Exception as e:
        print(f"[Perplexity] Exception: {e}")
        result = "No valid response from Perplexity."
        citations = None
    return result, citations

class CitationButtonView(discord.ui.View):
    def __init__(self, citations: list):
        super().__init__(timeout=120)
        for idx, url in enumerate(citations, start=1):
            self.add_item(discord.ui.Button(label=f"Citation {idx}", url=url, style=discord.ButtonStyle.link))

def setup(bot):
    bot.tree.add_command(perplexity_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="websearch", description="Search the web using Perplexity AI")
@app_commands.describe(query="Your search query")
async def perplexity_command(interaction: discord.Interaction, query: str):
    print(f"[Perplexity] Received interaction from {interaction.user} with query: {query}")
    thinking_embed = discord.Embed(
        title="🌐 Searching Perplexity...",
        description="Your query is being processed.",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Query", value=query[:1000], inline=False)
    await interaction.response.send_message(embed=thinking_embed)

    result, citations = perplexity_search(query)
    output_embed = discord.Embed(
        title="🔎 Perplexity AI Result",
        color=0x34a853
    )
    output_embed.add_field(name="Query", value=query[:1000], inline=False)
    if result:
        chunks = [result[i:i + 1024] for i in range(0, len(result), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            output_embed.add_field(
                name=f"Answer (Part {idx})" if len(chunks) > 1 else "Answer",
                value=chunk,
                inline=False
            )
    else:
        output_embed.add_field(name="Answer", value="No response from Perplexity.", inline=False)

    view = None
    if citations and isinstance(citations, list) and len(citations) > 0:
        view = CitationButtonView(citations)

    print(f"[Perplexity] Sending embed with {len(result) if result else 0} characters.")
    await interaction.edit_original_response(embed=output_embed, view=view)
