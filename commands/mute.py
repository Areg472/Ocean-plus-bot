import discord
from discord import app_commands
import datetime
from typing import Optional
from commands.utils import cooldown

def setup(bot):bot.tree.add_command(mute_command)

@app_commands.command(name="mute", description="Mute someone!")
@app_commands.checks.dynamic_cooldown(cooldown)
@app_commands.describe(
    user="The user you want to mute",
    reason="The reason for the mute",
    duration="The duration of the mute (in minutes)"
)
async def mute_command(interaction: discord.Interaction, user: discord.Member, duration: int, reason: Optional[str] = None):
    guildID = interaction.guild.id
    if guildID != 1183318046866149387:
        await interaction.response.send_message("This command is only available in the Ocean+ server!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You do not have permission to mute members.", ephemeral=True)
        return

    if duration <= 0:
        await interaction.response.send_message("Duration must be positive!", ephemeral=True)
        return

    try:
        reason_text = reason or "No reason provided"
        await user.timeout(datetime.timedelta(minutes=duration), reason=reason_text)

        await interaction.response.send_message(
            f"✅ {user.mention} has been muted for {duration} minutes.\nReason: {reason_text}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to mute this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)