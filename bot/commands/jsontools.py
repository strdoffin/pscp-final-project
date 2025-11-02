import discord
from discord import app_commands
from bot.commands import data_store

def register_json_tools(client: discord.Client, guild: discord.Object):
    # ===== Show iJudge entries =====
    @client.tree.command(
        name="showijudge",
        description="Show all iJudge rounds",
        guild=guild
    )
    async def show_ijudge(interaction: discord.Interaction):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        schedules = data_store.load_links()
        if not schedules:
            await interaction.response.send_message("ไม่พบรอบที่ลงไว้", ephemeral=True)
            return

        msg = "📋 **Ijudge Rounds:**\n"
        for idx, item in enumerate(schedules, 1):
            label = item.get("message") or item.get("link") or item.get("round", "Unknown")
            year = item.get("year", "????")
            month = item.get("month", "??")
            day = item.get("day", "??")
            hour = item.get("hour", 0)
            minute = item.get("minute", 0)

            msg += f"{idx}. `รอบที่ : {label}` เวลา `{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}`\n"

        await interaction.response.send_message(msg, ephemeral=True)
    # ===== Clear all iJudge entries =====
    @client.tree.command(
        name="clearijudge",
        description="Clear all iJudge rounds",
        guild=guild
    )
    async def clear_ijudge(interaction: discord.Interaction):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        data_store.save_links([])
        await interaction.response.send_message("✅ ลบรอบทั้งหมดเสร็จสิ้น", ephemeral=True)

    # ===== Clear specific iJudge entry by index =====
    @client.tree.command(
        name="clearijudge_index",
        description="Clear a specific iJudge round by index",
        guild=guild
    )
    @app_commands.describe(index="Index number of the round to delete (from /showijudge)")
    async def clear_ijudge_index(interaction: discord.Interaction, index: int):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        links = data_store.load_links()
        if index < 1 or index > len(links):
            await interaction.response.send_message("⚠️ หมายเลขรอบไม่ถูกต้อง", ephemeral=True)
            return

        removed = links.pop(index - 1)
        data_store.save_links(links)

        label = removed.get("round") or removed.get("message") or "Unknown"
        await interaction.response.send_message(f"✅ ลบรอบที่ `{label}` (index {index}) ออกจาก iJudge list แล้ว", ephemeral=True)

    # ===== Show Feedback schedules =====
    @client.tree.command(
        name="showfeedback",
        description="Show all Feedback schedules",
        guild=guild
    )
    async def show_feedback(interaction: discord.Interaction):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        schedules = data_store.load_schedules()
        if not schedules:
            await interaction.response.send_message("ℹ️ ไม่พบตาราง feed back", ephemeral=True)
            return

        msg = "📋 **Feedback Schedules:**\n"
        for idx, item in enumerate(schedules, 1):
            msg += f"{idx}. `{item['message']}` at `{item['year']}-{item['month']:02d}-{item['day']:02d} {item['hour']:02d}:{item['minute']:02d}`\n"

        await interaction.response.send_message(msg, ephemeral=True)

    # ===== Clear all Feedback schedules =====
    @client.tree.command(
        name="clearfeedback",
        description="Clear all Feedback schedules",
        guild=guild
    )
    async def clear_feedback(interaction: discord.Interaction):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        data_store.save_schedules([])
        await interaction.response.send_message("✅ ลบรอบ feed back ทั้งหมดเสร็จสิ้น", ephemeral=True)

    # ===== Clear specific Feedback schedule by index =====
    @client.tree.command(
        name="clearfeedback_index",
        description="Clear a specific Feedback schedule by index",
        guild=guild
    )
    @app_commands.describe(index="Index number of the feedback schedule to delete (from /showfeedback)")
    async def clear_feedback_index(interaction: discord.Interaction, index: int):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        schedules = data_store.load_schedules()
        if index < 1 or index > len(schedules):
            await interaction.response.send_message("⚠️ หมายเลขตาราง feedback ไม่ถูกต้อง", ephemeral=True)
            return

        removed = schedules.pop(index - 1)
        data_store.save_schedules(schedules)

        msg = removed.get("message") or "Unknown link"
        await interaction.response.send_message(f"✅ ตาราง feedback ที่ `{msg}` (index {index}) ถูกลบเรียบร้อยแล้ว", ephemeral=True)