import os
import requests
import discord
from discord import app_commands
from typing import Optional
import re

global_instruction = (
    "Provide a detailed and structured response under 2150 characters. "
    "Be concise when possible. Do not use headings (####, ###, ##, #) or bold text (**text**) for structure or emphasis."
)

def perplexity_search(query: str, context_size: str = "low"):
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
        "search_context_size": context_size,
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
        print(f"[Perplexity] Result: {result[:200]}...")
        citations = data.get("citations", None)
    except Exception as e:
        print(f"[Perplexity] Exception: {e}")
        result = "No valid response from Perplexity."
        citations = None
    used_citation_indices = set()
    if citations and isinstance(citations, list):
        matches = re.findall(r"\[(\d+)\]", result)
        for m in matches:
            idx = int(m)
            if 1 <= idx <= len(citations):
                used_citation_indices.add(idx)
        filtered_citations = [citations[i-1] for i in sorted(used_citation_indices)]
    else:
        filtered_citations = None
    return result, filtered_citations

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
@app_commands.describe(
    query="Your search query",
    context_size="Search context size: low (faster, cheaper) or medium (more accurate, more expensive)"
)
@app_commands.choices(context_size=[
    app_commands.Choice(name="Low (faster, cheaper)", value="low"),
    app_commands.Choice(name="Medium (more accurate, more expensive)", value="medium"),
])
async def perplexity_command(
    interaction: discord.Interaction,
    query: str,
    context_size: str = "low"
):
    print(f"[Perplexity] Received interaction from {interaction.user} with query: {query}, context_size: {context_size}")
    thinking_embed = discord.Embed(
        title="🌐 Searching Perplexity...",
        description="Your query is being processed.",
        color=0x4285f4
    )
    thinking_embed.add_field(name="Query", value=query[:1000], inline=False)
    thinking_embed.add_field(name="Context Size", value=context_size, inline=False)
    await interaction.response.send_message(embed=thinking_embed)

    result, citations = perplexity_search(query, context_size)
    output_embed = discord.Embed(
        title="🔎 Perplexity AI Result",
        color=0x34a853
    )
    output_embed.add_field(name="Query", value=query[:1000], inline=False)
    output_embed.add_field(name="Context Size", value=context_size, inline=False)
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
