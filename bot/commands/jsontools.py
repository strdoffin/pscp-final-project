"""Dynamic JSON Tools Management"""
import discord
from discord import app_commands
from bot.commands import data_store


def register_json_tools(client: discord.Client, guild: discord.Object):
    """Register dynamic JSON management commands for iJudge & Feedback"""

    # === Define data types and handlers ===
    json_configs = {
        "ijudge": {
            "load": data_store.load_links,
            "save": data_store.save_links,
            "title": "Ijudge Rounds",
            "label_key": ["round", "message", "link"],
            "no_data_msg": "ไม่พบรอบที่ลงไว้",
            "cleared_msg": "✅ ลบรอบทั้งหมดเสร็จสิ้น",
            "clear_item_msg": "✅ ลบรอบที่ `{label}` (index {index}) ออกจาก iJudge list แล้ว",
            "invalid_index_msg": "⚠️ หมายเลขรอบไม่ถูกต้อง",
        },
        "feedback": {
            "load": data_store.load_schedules,
            "save": data_store.save_schedules,
            "title": "Feedback Schedules",
            "label_key": ["message"],
            "no_data_msg": "ℹ️ ไม่พบตาราง feed back",
            "cleared_msg": "✅ ลบรอบ feed back ทั้งหมดเสร็จสิ้น",
            "clear_item_msg": "✅ ตาราง feedback ที่ `{label}` (index {index}) ถูกลบเรียบร้อยแล้ว",
            "invalid_index_msg": "⚠️ หมายเลขตาราง feedback ไม่ถูกต้อง",
        },
    }

    # === Helper to check TA role ===
    async def check_ta(interaction: discord.Interaction) -> bool:
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True
            )
            return False
        return True

    # === Factory for show command ===
    def make_show_command(key: str, cfg: dict):
        @client.tree.command(
            name=f"show{key}",
            description=f"Show all {cfg['title']}",
            guild=guild,
        )
        async def show_command(interaction: discord.Interaction):
            if not await check_ta(interaction):
                return

            data = cfg["load"]()
            if not data:
                await interaction.response.send_message(cfg["no_data_msg"], ephemeral=True)
                return

            msg = f"📋 **{cfg['title']}:**\n"
            for idx, item in enumerate(data, 1):
                label = next((item.get(k) for k in cfg["label_key"] if item.get(k)), "Unknown")
                year = item.get("year", "????")
                month = item.get("month", "??")
                day = item.get("day", "??")
                hour = item.get("hour", 0)
                minute = item.get("minute", 0)
                msg += f"{idx}. `{label}` เวลา `{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}`\n"

            await interaction.response.send_message(msg, ephemeral=True)

    # === Factory for clear all command ===
    def make_clear_all_command(key: str, cfg: dict):
        @client.tree.command(
            name=f"clear{key}",
            description=f"Clear all {cfg['title']}",
            guild=guild,
        )
        async def clear_all(interaction: discord.Interaction):
            if not await check_ta(interaction):
                return

            cfg["save"]([])
            await interaction.response.send_message(cfg["cleared_msg"], ephemeral=True)

    # === Factory for clear by index command ===
    def make_clear_index_command(key: str, cfg: dict):
        @client.tree.command(
            name=f"clear{key}_index",
            description=f"Clear specific {cfg['title']} by index",
            guild=guild,
        )
        @app_commands.describe(index="Index number from /show command")
        async def clear_index(interaction: discord.Interaction, index: int):
            if not await check_ta(interaction):
                return

            items = cfg["load"]()
            if index < 1 or index > len(items):
                await interaction.response.send_message(cfg["invalid_index_msg"], ephemeral=True)
                return

            removed = items.pop(index - 1)
            cfg["save"](items)

            label = next((removed.get(k) for k in cfg["label_key"] if removed.get(k)), "Unknown")
            msg = cfg["clear_item_msg"].format(label=label, index=index)
            await interaction.response.send_message(msg, ephemeral=True)

    # === Register all commands ===
    for key, cfg in json_configs.items():
        make_show_command(key, cfg)
        make_clear_all_command(key, cfg)
        make_clear_index_command(key, cfg)
