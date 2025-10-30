import discord
from discord import app_commands
from bot.commands import data_store
from datetime import datetime

def register_ijudge_link(client: discord.Client, guild: discord.Object):

    @client.tree.command(name="ijudge", description="add deadline of ijudge rounds", guild=guild)
    @app_commands.describe(
        rounds="what's rounds ex. (round 1, round 2, ...)",
        day="Release day in YYYY-MM-DD format"
    )
    async def ijudge_command(interaction: discord.Interaction, rounds: str, day: str):
        # Validate day format
        if interaction.user.roles is None or not any(role.name == "staff" for role in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        try:
            release_date = datetime.strptime(day, "%Y-%m-%d").date()
        except ValueError:
            await interaction.response.send_message("❌ Invalid date format. Use YYYY-MM-DD.",ephemeral=True)
            return

        # Load existing links
        roundss = data_store.load_links()
        roundss.append({"round": rounds, "day": day})
        data_store.save_links(roundss)

        await interaction.response.send_message(f"✅ Saved round : `{rounds}` for `{day}`",ephemeral=True)
