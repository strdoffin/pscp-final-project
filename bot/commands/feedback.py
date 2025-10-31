import discord
from discord import app_commands
from bot.commands import data_store
from datetime import datetime

def register_add_schedule(client: discord.Client, guild: discord.Object):
    @client.tree.command(
        name="addschedule",
        description="Add a new notification to the schedule JSON",
        guild=guild
    )
    @app_commands.describe(
        date="Date in YYYY-MM-DD format",
        hour="Hour in 24h format (0-23)",
        minute="Minute (0-59)",
        message="Message to send"
    )
    async def addschedule_command(
        interaction: discord.Interaction,
        date: str,
        hour: int,
        minute: int,
        message: str
    ):
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Hour or minute out of range")
        except ValueError:
            await interaction.response.send_message("❌ Invalid date format. Use YYYY-MM-DD. Hour must be 0-23 and minute must be 0-59.", ephemeral=True)
            return

        # Load current schedules
        schedules = data_store.load_schedules()

        # Append new schedule
        schedules.append({
            "datetime": date,
            "hour": hour,
            "minute": minute,
            "message": message
        })

        # Save back to JSON
        data_store.save_schedules(schedules)

        await interaction.response.send_message(
            f"✅ Added new notification for {date} at {hour:02d}:{minute:02d}"
        )
