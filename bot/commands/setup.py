"""/setup"""
import discord
from discord import app_commands
from bot.commands import data_store

def register_setup_command(client: discord.Client, guild: discord.Object):
    """
    Registers the /addfeedback command, which allows authorized users (TAs)
    to schedule a feedback notification that will later be sent automatically.
    """

    @client.tree.command(
        name="setup",
        description="setup channel to sent notification",
        guild=guild
    )
    async def setup_command(interaction: discord.Interaction):
        # ===== Permission Check =====
        # Only users with the "TA" role are allowed to use this command
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (เฉพาะ TA เท่านั้น)",
                ephemeral=True
            )
            return
        channel_id = interaction.channel_id
        data_store.save_setup(channel_id)  # store as a single integer

        # ===== Response =====
        await interaction.response.send_message(
            f"✅ ตั้งค่าช่องแจ้งเตือนเรียบร้อย! Notifications จะถูกส่งที่ <#{channel_id}>",
            ephemeral=True
        )
