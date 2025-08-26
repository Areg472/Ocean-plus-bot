import discord
from discord import app_commands
import wikipediaapi
from commands.utils import cooldown, get_ai_response

class WikipediaSummaryView(discord.ui.View):
    def __init__(self, page):
        super().__init__(timeout=300)
        self.page = page
    
    @discord.ui.button(label="AI Article Summary", style=discord.ButtonStyle.secondary, emoji="🤖")
    async def article_summary(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        article_prompt = f"""Summarize this Wikipedia article about "{self.page.title}":

{self.page.text}

Provide a comprehensive but concise summary that covers the main points, key facts, and important details. Keep it under 1500 characters and make it engaging and informative."""

        waiting_embed = discord.Embed(
            title="🤔 Analyzing article...",
            description="Generating AI article summary with Mistral...",
            color=0x4285f4
        )
        waiting_message = await interaction.followup.send(embed=waiting_embed, ephemeral=True)
        
        try:
            ai_response = await get_ai_response(
                question=article_prompt,
                model="mistral-small-2506"
            )
            
            if isinstance(ai_response, tuple):
                summary_text = ai_response[0]
            else:
                summary_text = ai_response
                
            summary_embed = discord.Embed(
                title=f"AI Summary: {self.page.title}",
                description=summary_text,
                url=self.page.fullurl,
                colour=discord.Colour.green()
            )
            summary_embed.set_footer(text="Powered by Mistral AI")
            
            await waiting_message.edit(embed=summary_embed)
            
        except Exception as e:
            print(f"Wikipedia AI summary error for user {interaction.user.id}: {str(e)}")
            error_embed = discord.Embed(
                title="Summary Error",
                description="Sorry, I couldn't generate an article summary at the moment. Please try again later.",
                colour=discord.Colour.red()
            )
            await waiting_message.edit(embed=error_embed)

def setup(bot):
    bot.tree.add_command(wiki_search_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="wikipedia", description="Search wikipedia articles")
@app_commands.describe(query="The search query")
@app_commands.checks.dynamic_cooldown(cooldown)
async def wiki_search_command(interaction: discord.Interaction, query: str):
    wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent='DiscordBot/1.0'
    )

    try:
        page = wiki.page(query)

        if page.exists():
            if page.summary <= page.summary[:300]:
                embed = discord.Embed(
                    title=page.title,
                    url=page.fullurl,
                    description=page.summary,
                    color=discord.Color.blue()
                )
            elif page.summary > page.summary[:300]:
                embed = discord.Embed(
                    title=page.title,
                    url=page.fullurl,
                    description=page.summary[:300] + "...",
                    color=discord.Color.blue()
                )
            
            view = WikipediaSummaryView(page)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(f"Could not find Wikipedia article for '{query}'", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)