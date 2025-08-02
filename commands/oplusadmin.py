import discord
from discord import app_commands
from commands.utils import cooldown

def setup(bot):bot.tree.add_command(oplusadmin_command)

@app_commands.command(name="oplusadmin", description="Make someone an O+ admin!")
@app_commands.checks.dynamic_cooldown(cooldown)
@app_commands.describe(
    user="The user you want to make an admin",
    reason="The reason for the promotion",
)
async def oplusadmin_command(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return

    guildID = interaction.guild.id
    if guildID != 1183318046866149387:
        await interaction.response.send_message("This command is only available in the Ocean+ server!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You need manage roles permissions to make people O+ admins.", ephemeral=True)
        return

    try:
        role = discord.utils.get(interaction.guild.roles, name="Ocean+ admin")
        if not role:
            await interaction.response.send_message("The Ocean+ admin role could not be found!", ephemeral=True)
            return

        if role in user.roles:
            await interaction.response.send_message(f"{user.mention} is already an Ocean+ Admin!", ephemeral=True)
            return

        await user.add_roles(role)
        reason_text = reason or "No reason provided"
        await interaction.response.send_message(
            f"✅ {user.mention} has been made an Ocean+ Admin.\nReason: {reason_text}",
            ephemeral=False
        )

    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to manage roles!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)