import discord
from discord import app_commands
from commands.utils import cooldown

def setup(bot):
    bot.tree.add_command(help_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.command(name="help", description="Help you out with commands!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def help_command(interaction: discord.Interaction):
    commands_list = [
        ("/quote", "Get a random quote"),
        ("/meme", "Get a random meme"),
        ("/date", "Get the current date and days until the next Ocean+ anniversary"),
        ("/got_a_life", "Check if you have a life or not"),
        ("/duck", "Get a cute duck picture"),
        ("/dad_joke", "Generates a random dad joke"),
        ("/prompt", "Ask me anything, powered by AI"),
        ("/translate", "Translate any text to any languages!"),
        ("/cat", "Sends a cute cat picture!"),
        ("/8ball", "Fortune teller!"),
        ("/mock", "Make your message wEirD aS hEll"),
        ("/weather", "Check the weather for the specified location or check forecast!"),
        ("/text_to_morse", "Translate text to morse code!"),
        ("/boardgame", "Search for board games on BoardGameGeek"),
        ("/websearch", "Search the web using Perplexity AI"),
        ("Ask AI (Context menu)", "Transcribe and ask AI about voice messages"),
        ("Transcribe Message (Context menu)", "Transcribe voice messages to text"),
        ("/gamble", "Randomly gamble!"),
        ("/wikipedia", "Search wikipedia articles"),
        ("/pet", "Pet the mentioned user!"),
        ("/jail", "Put the mentioned user in jail!"),
        ("/github", "Get github info of a user"),
        ("/joke_overhead", "Use this and mention the guy that doesn't understand jokes!"),
        ("/bonk", "Bonk the mentioned person!"),
        ("/hi", "Say hi to the bot!"),
    ]

    pages = []
    for i in range(0, len(commands_list), 6):
        page_commands = commands_list[i:i+6]
        embed = discord.Embed(
            title="Ocean+ Help",
            url="https://oceanbluestream.com/",
            description=f"Page {len(pages)+1}/{-(-len(commands_list)//6)}", 
            colour=discord.Colour.dark_blue()
        )

        for cmd, desc in page_commands:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.set_footer(text="Made by Areg, the creator of Ocean+. Thanks to Its_Padar for helping me with the code, make sure to give him a follow on BlueSky!")
        pages.append(embed)

    class HelpView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            self.current_page = 0

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = (self.current_page - 1) % len(pages)
            await interaction.response.edit_message(embed=pages[self.current_page])

        @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = (self.current_page + 1) % len(pages)
            await interaction.response.edit_message(embed=pages[self.current_page])

    view = HelpView()
    await interaction.response.send_message(embed=pages[0], view=view)