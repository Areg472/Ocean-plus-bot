import os
import requests
import discord
from discord import app_commands
from typing import Optional
import re
import socket
from urllib.parse import urlparse
from .utils import moderate_content

global_instruction = (
    "Provide a detailed and structured response under 2150 characters. "
    "Be concise when possible. Do not use headings (####, ###, ##, #) or bold text (**text**) for structure or emphasis."
)

def perplexity_search(query: str, context_size: str = "low", search_domain_filter: Optional[list] = None):
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
        **({"search_domain_filter": search_domain_filter} if search_domain_filter else {}),
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
        filtered_citations = [(i, citations[i-1]) for i in sorted(used_citation_indices)]
    else:
        filtered_citations = None
    return result, filtered_citations

class CitationButtonView(discord.ui.View):
    def __init__(self, filtered_citations: list):
        super().__init__(timeout=120)
        for citation_number, url in filtered_citations:
            self.add_item(discord.ui.Button(label=f"Citation {citation_number}", url=url, style=discord.ButtonStyle.link))

def setup(bot):
    bot.tree.add_command(perplexity_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="websearch", description="Search the web using Perplexity AI")
@app_commands.describe(
    query="Your search query",
    context_size="Search context size",
    search_domain_filter="Comma-separated allowlist of domains/URLs (e.g. wikipedia.org, wsj.com, https://en.m.wikipedia.org/wiki/United_States)"
)
@app_commands.choices(context_size=[
    app_commands.Choice(name="Low (faster, cheaper)", value="low"),
    app_commands.Choice(name="Medium (more accurate, more expensive)", value="medium"),
])
async def perplexity_command(
    interaction: discord.Interaction,
    query: str,
    context_size: str = "low",
    search_domain_filter: Optional[str] = None
):
    if len(query) > 3000:
        input_limit = True
    else:
        input_limit = False

    print(f"[Perplexity] Received interaction from {interaction.user} with query: {query}, context_size: {context_size}, search_domain_filter: {search_domain_filter}")
    thinking_embed = discord.Embed(
        title="🌐 Searching Perplexity...",
        description="Your query is being processed.",
        color=0x4285f4
    )
    if len(query) > 1024:
        chunks = [query[i:i + 1024] for i in range(0, len(query), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            thinking_embed.add_field(name=f"Query (Part {idx})", value=chunk, inline=False)
    else:
        thinking_embed.add_field(name="Query", value=query, inline=False)
    await interaction.response.send_message(embed=thinking_embed)

    domain_list = None
    if search_domain_filter:
        domain_list = [d.strip() for d in search_domain_filter.split(",") if d.strip()]
        if not domain_list:
            await interaction.response.send_message("Error: No valid domains or URLs provided.", ephemeral=True)
            return
        invalid_domains = [d for d in domain_list if not is_valid_domain_or_url(d)]
        if invalid_domains:
            await interaction.response.send_message(
                f"Error: Invalid or non-existent domains/URLs: {', '.join(invalid_domains)}", ephemeral=True
            )
            return
        
    moderation_flagged = await moderate_content(query)
    
    if moderation_flagged or input_limit:
        result = None
        filtered_citations = None
    else:
        result, filtered_citations = perplexity_search(query, context_size, domain_list)
    output_embed = discord.Embed(
        title="🔎 Perplexity AI Result",
        color=0x34a853
    )
    if len(query) > 1024:
        chunks = [query[i:i + 1024] for i in range(0, len(query), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            output_embed.add_field(name=f"Query (Part {idx})", value=chunk, inline=False)
    else:
        output_embed.add_field(name="Query", value=query, inline=False)
    if result:
        chunks = [result[i:i + 1024] for i in range(0, len(result), 1024)]
        for idx, chunk in enumerate(chunks, start=1):
            output_embed.add_field(
                name=f"Answer (Part {idx})" if len(chunks) > 1 else "Answer",
                value=chunk,
                inline=False
            )
    elif input_limit:
        output_embed.add_field(
            name="Answer", 
            value="Input exceeds the 3000 character limit. Please shorten your message.",
            inline=False
        )
    elif moderation_flagged:
        output_embed.add_field(
            name="Answer", 
            value="Your message has been flagged by our content moderation system lol(OpenAI model btw). Please revise your input.",
            inline=False
        )
    else:
        output_embed.add_field(name="Answer", value="No response from Perplexity.", inline=False)

    view = None
    if filtered_citations and isinstance(filtered_citations, list) and len(filtered_citations) > 0:
        view = CitationButtonView(filtered_citations)
    print(f"[Perplexity] Sending embed with {len(result) if result else 0} characters.")
    await interaction.edit_original_response(embed=output_embed, view=view)

def is_valid_domain_or_url(item: str) -> bool:
    domain = item
    if item.startswith("http://") or item.startswith("https://"):
        try:
            parsed = urlparse(item)
            domain = parsed.netloc
            if not domain:
                return False
        except Exception:
            return False
    domain = domain.split(":")[0]
    if not re.match(r"^(?!-)[A-Za-z0-9-\.]{1,1000}\.[A-Za-z]{2,}$", domain):
        return False
    try:
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False
        return False
