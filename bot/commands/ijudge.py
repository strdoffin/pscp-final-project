"""/ijudge"""
import discord
from discord import app_commands
from bot.commands import data_store
from datetime import datetime


def register_ijudge_link(client: discord.Client, guild: discord.Object) -> None:
    """
    Register the /addijudge command for adding iJudge round deadlines
    (Thailand time). Only users with the "TA" role can use this command.
    """

    @client.tree.command(
        name="addijudge",
        description="Add iJudge round deadline (Thailand time)",
        guild=guild,
    )
    @app_commands.describe(
        round="Round name (e.g. Round 1, Final, etc.)",
        date="Date in YYYY-MM-DD",
        hour="Hour (0–23)",
        minute="Minute (0–59)",
    )
    async def add_ijudge_command(
        interaction: discord.Interaction,
        round: str,
        date: str,
        hour: int,
        minute: int,
    ) -> None:
        """
        Handle the /addijudge command.

        Steps:
        1. Check TA permission.
        2. Validate date/time format.
        3. Save iJudge round deadline to JSON storage.
        """

        # ===== Permission Check =====
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (เฉพาะ TA เท่านั้น)",
                ephemeral=True,
            )
            return

        # ===== Date & Time Validation =====
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                (
                    "❌ รูปแบบข้อมูลวันเวลาไม่ถูกต้อง "
                    "(ใช้รูปแบบ YYYY-MM-DD และเวลา 0–23 / 0–59)"
                ),
                ephemeral=True,
            )
            return

        # ===== Load, Update, and Save Data =====
        links = data_store.load_links()
        links.append(
            {
                "round": round,
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": hour,
                "minute": minute,
            }
        )
        data_store.save_links(links)

        # ===== Confirmation Message =====
        await interaction.response.send_message(
            (
                f"✅ เพิ่มรอบ iJudge `{round}` เวลา "
                f"`{dt.year}-{dt.month:02d}-{dt.day:02d} "
                f"{hour:02d}:{minute:02d}` (เวลาไทย)"
            ),
            ephemeral=True,
        )
