"""/addfeedback"""
from datetime import datetime
import discord
from discord import app_commands
from bot.commands import data_store



def register_feedback_schedule(client: discord.Client, guild: discord.Object):
    """
    Registers the /addfeedback command, which allows authorized users (TAs)
    to schedule a feedback notification that will later be sent automatically.
    """

    @client.tree.command(
        name="addfeedback",
        description="Add a new feedback notification",
        guild=guild
    )
    @app_commands.describe(
        date="Date in YYYY-MM-DD format",
        hour="Hour (0-23)",
        minute="Minute (0-59)",
        link="Link to send"
    )
    async def addfeedback_command(
        interaction: discord.Interaction,
        date: str,
        hour: int,
        minute: int,
        link: str
    ):
        """
        Handles the /addfeedback command:
        - Checks TA permissions
        - Validates date/time format
        - Saves the new feedback schedule to JSON
        """

        # ===== Permission Check =====
        # Only users with the "TA" role are allowed to use this command
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (เฉพาะ TA เท่านั้น)",
                ephemeral=True
            )
            return

        # ===== Date & Time Validation =====
        try:
            # Parse the provided date
            dt = datetime.strptime(date, "%Y-%m-%d")

            # Ensure valid hour and minute range
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError

        except ValueError:
            await interaction.response.send_message(
                "❌ รูปแบบข้อมูลวันเวลาไม่ถูกต้อง (ใช้รูปแบบ YYYY-MM-DD และเวลา 0–23/0–59)",
                ephemeral=True
            )
            return

        # ===== Load & Save Schedule =====
        schedules = data_store.load_schedules()

        # Add new schedule entry
        schedules.append({
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": hour,
            "minute": minute,
            "message": link
        })

        # Save to JSON
        data_store.save_schedules(schedules)

        # ===== Response =====
        await interaction.response.send_message(
            f"✅ เพิ่มการแจ้งเตือน feedback สำหรับ `{date} {hour:02d}:{minute:02d}`",
            ephemeral=True
        )
