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

    # ===== Clear specific iJudge entry =====
    @client.tree.command(
        name="clearijudge_round",
        description="Clear a specific iJudge round by name",
        guild=guild
    )
    @app_commands.describe(round="Round name to delete")
    async def clear_ijudge_round(interaction: discord.Interaction, round: str):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        links = data_store.load_links()
        new_links = [item for item in links if item["round"].lower() != round.lower()]

        if len(new_links) == len(links):
            await interaction.response.send_message(f"⚠️ ไม่พบรอบที่ `{round}`", ephemeral=True)
            return

        data_store.save_links(new_links)
        await interaction.response.send_message(f"✅ รอบที่ `{round}` ถูกลบออกจาก iJudge list.", ephemeral=True)

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

    # ===== Clear specific Feedback schedule by link =====
    @client.tree.command(
        name="clearfeedback_link",
        description="Clear a specific Feedback schedule by link",
        guild=guild
    )
    @app_commands.describe(link="Exact link to delete")
    async def clear_feedback_link(interaction: discord.Interaction, link: str):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return

        schedules = data_store.load_schedules()
        # compare with the 'message' field which now stores the link
        new_schedules = [item for item in schedules if item["message"].lower() != link.lower()]

        if len(new_schedules) == len(schedules):
            await interaction.response.send_message(f"⚠️ ไม่พบตาราง feed back ที่ลิ้งค์ `{link}`", ephemeral=True)
            return

        data_store.save_schedules(new_schedules)
        await interaction.response.send_message(f"✅ ตาราง feed back ที่ลิ้งค์ `{link}` ได้ถูกลบ", ephemeral=True)
