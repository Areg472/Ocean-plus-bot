"""import discord
from discord import app_commands
from commands.utils import cooldown
import secrets
import string
import asyncio

user_codes = {}

class ContextSelectionView(discord.ui.View):
    def __init__(self, code: str, user_id: int):
        super().__init__(timeout=30)
        self.code = code
        self.user_id = user_id

    @discord.ui.button(label="Context 1(whiplash truth)", style=discord.ButtonStyle.secondary, emoji="1️⃣")
    async def context_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_codes[self.user_id] = {"code": self.code, "context": 1}
        await interaction.response.edit_message(
            content=f"🔑 **Your Ocean+ access code:** `{self.code}`\n\n"
                   f"**Selected Context:** 1\n"
                   f"Use this code in the designated channel to get your Ocean+ link!\n"
                   f"*Note: This code is unique to you and will expire in 30 seconds or after use.*",
            view=None
        )

    @discord.ui.button(label="Context 2(tim hortons)", style=discord.ButtonStyle.secondary, emoji="2️⃣")
    async def context_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_codes[self.user_id] = {"code": self.code, "context": 2}
        await interaction.response.edit_message(
            content=f"🔑 **Your Ocean+ access code:** `{self.code}`\n\n"
                   f"**Selected Context:** 2\n"
                   f"Use this code in the designated channel to get your Ocean+ link!\n"
                   f"*Note: This code is unique to you and will expire in 30 seconds or after use.*",
            view=None
        )

    async def on_timeout(self):
        if self.user_id in user_codes:
            del user_codes[self.user_id]

async def reset_user_code(user_id, delay=30):
    await asyncio.sleep(delay)
    if user_id in user_codes:
        del user_codes[user_id]

def generate_user_code():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

def setup(bot):
    bot.tree.add_command(generate_code_command)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(dms=True, private_channels=True)  # DM only
@app_commands.command(name="generate_code", description="Generate a unique code for Ocean+ access!")
@app_commands.checks.dynamic_cooldown(cooldown)
async def generate_code_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    new_code = generate_user_code()

    view = ContextSelectionView(new_code, user_id)
    asyncio.create_task(reset_user_code(user_id, 30))

    await interaction.response.send_message(
        f"🔑 **Your Ocean+ access code:** `{new_code}`\n\n"
        f"**Please select a context:**",
        view=view,
        ephemeral=True
    )"""
