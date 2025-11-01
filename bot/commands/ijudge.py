import discord
from discord import app_commands
from bot.commands import data_store
from datetime import datetime

def register_ijudge_link(client: discord.Client, guild: discord.Object):
    @client.tree.command(
        name="ijudge",
        description="Add iJudge round deadline (Thailand time)",
        guild=guild
    )
    @app_commands.describe(
        round="Round name (e.g. Round 1, Final, etc.)",
        date="Date in YYYY-MM-DD",
        hour="Hour (0-23)",
        minute="Minute (0-59)"
    )
    async def ijudge_command(
        interaction: discord.Interaction, 
        round: str, 
        date: str, 
        hour: int, 
        minute: int
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

        links = data_store.load_links()
        links.append({
            "round": round,
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": hour,
            "minute": minute
        })
        data_store.save_links(links)

        await interaction.response.send_message(
            f"✅ เพิ่ม iJudge รอบที่ `{round}` เวลา `{dt.year}-{dt.month:02d}-{dt.day:02d} {hour:02d}:{minute:02d}` (Thailand)",
            ephemeral=True
        )
