import discord
from discord import app_commands
from bot.commands import data_store
from datetime import datetime

def register_feedback_schedule(client: discord.Client, guild: discord.Object):
    @client.tree.command(
        name="addfeedback",
        description="Add a new feedback notification",
        guild=guild
    )
    @app_commands.describe(
        date="Date in YYYY-MM-DD",
        hour="Hour (0-23)",
        minute="Minute (0-59)",
        link="link to send"
    )
    async def addschedule_command(
        interaction: discord.Interaction,
        date: str,
        hour: int,
        minute: int,
        link: str
    ):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ รูปแบบข้อมูลวันเวลาไม่ถูกต้อง", ephemeral=True)
            return

        schedules = data_store.load_schedules()
        schedules.append({
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": hour,
            "minute": minute,
            "message": link
        })
        data_store.save_schedules(schedules)

        await interaction.response.send_message(
            f"✅ เพิ่ม feedback notification สำหรับ `{date} {hour:02d}:{minute:02d}`",
            ephemeral=True
        )
