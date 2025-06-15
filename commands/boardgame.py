import discord
from discord import app_commands
import requests
import xml.etree.ElementTree as ET
import html
import time
from commands.utils import cooldown

def setup(bot):
    """
    Register the boardgame command with the bot
    """
    bot.tree.add_command(boardgame_command)

class BoardGameView(discord.ui.View):
    def __init__(self, embeds, author):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.author = author
        self.current_page = 0
        
        if len(embeds) <= 1:
            for child in self.children:
                child.disabled = True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        try:
            await self.message.edit(view=self)
        except:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the person who ran this command can use these buttons.",
                                                    ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="boardgame", description="Search for board games on BoardGameGeek")
@app_commands.describe(query="The name of the board game to search for")
@app_commands.checks.dynamic_cooldown(cooldown)
async def boardgame_command(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    try:
        search_url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"
        response = requests.get(search_url)

        if response.status_code != 200:
            await interaction.followup.send(
                f"Error: Could not connect to BoardGameGeek API. Status code: {response.status_code}")
            return

        root = ET.fromstring(response.content)
        items = root.findall('.//item')

        if not items:
            await interaction.followup.send(f"No board games found matching '{query}'.")
            return

        items = items[:15]
        total_results = len(items)

        game_ids = [item.get('id') for item in items]
        details_url = f"https://boardgamegeek.com/xmlapi2/thing?id={','.join(game_ids)}&stats=1"
        details_response = requests.get(details_url)

        if details_response.status_code == 202:
            await interaction.followup.send("Processing your request... Please try again in a few seconds.",
                                            ephemeral=True)
            time.sleep(2)
            details_response = requests.get(details_url)

        if details_response.status_code != 200:
            await interaction.followup.send(
                f"Error: Could not retrieve game details. Status code: {details_response.status_code}")
            return

        details_root = ET.fromstring(details_response.content)
        game_details = {}

        for item in details_root.findall('.//item'):
            game_id = item.get('id')
            description = item.find('.//description')
            description_text = description.text if description is not None and description.text else "No description available."
            
            # Decode HTML entities in the description
            description_text = html.unescape(description_text)

            if len(description_text) > 200:
                description_text = description_text[:197] + "..."

            rating_element = item.find('.//statistics/ratings/average')
            rating = rating_element.get('value') if rating_element is not None else "N/A"

            min_players_element = item.find('.//minplayers')
            max_players_element = item.find('.//maxplayers')
            min_players = min_players_element.get('value') if min_players_element is not None else "?"
            max_players = max_players_element.get('value') if max_players_element is not None else "?"

            playtime_element = item.find('.//playingtime')
            playtime = playtime_element.get('value') if playtime_element is not None else "?"

            game_details[game_id] = {
                'description': description_text,
                'rating': rating,
                'players': f"{min_players}-{max_players}" if min_players != max_players else min_players,
                'playtime': playtime
            }

        embeds = []

        if total_results <= 5:
            embed = discord.Embed(
                title=f" BoardGameGeek Search Results for '{query}'",
                color=discord.Color.blue(),
                description=f"Found {total_results} result(s)"
            )

            for item in items:
                game_id = item.get('id')
                name_element = item.find('name')
                game_name = html.unescape(name_element.get('value')) if name_element is not None else "Unknown"
                year_published = item.find('yearpublished')
                year = year_published.get('value') if year_published is not None else "N/A"

                bgg_link = f"https://boardgamegeek.com/boardgame/{game_id}"

                if game_id in game_details:
                    details = game_details[game_id]
                    description = details['description']
                    info_line = f"⭐ {details['rating']}/10 •  {details['players']} players • ⏱️ {details['playtime']} min"
                    value_text = f"{description}\n\n{info_line}\n[View on BoardGameGeek]({bgg_link})"
                else:
                    value_text = f"[View on BoardGameGeek]({bgg_link})"

                embed.add_field(
                    name=f"{game_name} ({year})",
                    value=value_text,
                    inline=False
                )

            embed.set_footer(text="Data from BoardGameGeek")
            embeds.append(embed)
        else:
            for page in range((total_results + 4) // 5):
                start_idx = page * 5
                end_idx = min(start_idx + 5, total_results)
                page_items = items[start_idx:end_idx]

                embed = discord.Embed(
                    title=f" BoardGameGeek Search Results for '{query}'",
                    color=discord.Color.blue(),
                    description=f"Found {total_results} result(s)"
                )

                for item in page_items:
                    game_id = item.get('id')
                    name_element = item.find('name')
                    game_name = html.unescape(name_element.get('value')) if name_element is not None else "Unknown"
                    year_published = item.find('yearpublished')
                    year = year_published.get('value') if year_published is not None else "N/A"

                    bgg_link = f"https://boardgamegeek.com/boardgame/{game_id}"

                    if game_id in game_details:
                        details = game_details[game_id]
                        description = details['description']
                        info_line = f"⭐ {details['rating']}/10 •  {details['players']} players • ⏱️ {details['playtime']} min"
                        value_text = f"{description}\n\n{info_line}\n[View on BoardGameGeek]({bgg_link})"
                    else:
                        value_text = f"[View on BoardGameGeek]({bgg_link})"

                    embed.add_field(
                        name=f"{game_name} ({year})",
                        value=value_text,
                        inline=False
                    )

                embed.set_footer(text=f"Page {page + 1}/{(total_results + 4) // 5} • Data from BoardGameGeek")
                embeds.append(embed)

        view = BoardGameView(embeds, interaction.user)
        message = await interaction.followup.send(embed=embeds[0], view=view)
        view.message = message

    except Exception as e:
        await interaction.followup.send(f"An error occurred while searching for board games: {str(e)}")