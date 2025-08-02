import discord
from discord import app_commands
from typing import Optional
from commands.utils import cooldown

def setup(bot):
    bot.tree.add_command(ban_command)

@app_commands.command(name="ban", description="Ban someone!")
@app_commands.checks.dynamic_cooldown(cooldown)
@app_commands.describe(
    user="The user you want to ban",
    reason="The reason for the ban",
    delete_days="The messages you want to be deleted in days."
)
async def ban_command(interaction: discord.Interaction, user: discord.Member, delete_days: Optional[int] = None, reason: Optional[str] = None):
    guildID = interaction.guild.id
    if guildID != 1183318046866149387:
        await interaction.response.send_message("This command is only available in the Ocean+ server!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You do not have permission to ban members.", ephemeral=True)
        return

    if delete_days is not None and (delete_days < 0 or delete_days > 7):
        await interaction.response.send_message("Delete days must be between 0 and 7!", ephemeral=True)
        return

    try:
        reason_text = reason or "No reason provided"
        await user.ban(delete_message_days=delete_days, reason=reason_text)
        await interaction.response.send_message(
            f"✅ {user.mention} has been banned.\nReason: {reason_text}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)