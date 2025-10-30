import discord
from discord import app_commands
from bot.commands import data_store
from datetime import datetime

def register_feedback_link(client: discord.Client, guild: discord.Object):

    @client.tree.command(name="feedback", description="Submit a feedback link with release day", guild=guild)
    @app_commands.describe(
        link="The link to submit",
        day="Release day in YYYY-MM-DD format"
    )
    async def feedback_command(interaction: discord.Interaction, link: str, day: str):
        # Validate day format
        try:
            release_date = datetime.strptime(day, "%Y-%m-%d").date()
        except ValueError:
            await interaction.response.send_message("❌ Invalid date format. Use YYYY-MM-DD.")
            return

        # Load existing links
        links = data_store.load_links()
        links.append({"link": link, "day": day})
        data_store.save_links(links)

        await interaction.response.send_message(f"✅ Saved link `{link}` for `{day}`")
