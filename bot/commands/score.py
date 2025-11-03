"""/score"""
import discord
import pandas as pd
import asyncio
from discord import app_commands
from discord.ext import commands

# 🔹 Google Sheet ตั้งค่า
SHEET_ID = "1ydK3l7Lks3p57Tmvxrhk3dqu5dVcOmNgBetvVrWnNyk"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=861657501"


# ================================================================
# 🔹 ฟังก์ชันอ่านข้อมูลคะแนนจาก Google Sheet
# ================================================================
def get_student_score(student_id: str):
    try:
        df = pd.read_csv(SHEET_URL, header=0)

        # อ่านสถิติจากแถว 1-2 (O2:R3)
        try:
            stats = {
                "min_name": df.iloc[0, 14],
                "max_name": df.iloc[0, 15],
                "avg_name": df.iloc[0, 16],
                "sd_name":  df.iloc[0, 17],

                "min_val": df.iloc[1, 14],
                "max_val": df.iloc[1, 15],
                "avg_val": df.iloc[1, 16],
                "sd_val":  df.iloc[1, 17],
            }
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการอ่านสถิติ (O2:R3): {e}")
            stats = None

        # คอลัมน์หลัก
        id_col = df.columns[0]
        name_col = df.columns[1]
        total_col = df.columns[11]

        # เตรียมข้อมูล
        df[id_col] = df[id_col].astype(str)
        student_id = str(student_id)

        # ข้ามแถวสถิติ (2 แถวแรก)
        student_df = df.iloc[2:].copy()
        student_df[id_col] = student_df[id_col].astype(str)

        # ค้นหานักเรียนตามรหัส
        result_row = student_df[student_df[id_col] == student_id]

        if result_row.empty:
            return (None, stats)

        student_data = result_row.iloc[0]

        # ดึงคะแนนย่อย (C ถึง K)
        score_columns = df.columns[2:11]
        detailed_scores = {}
        for col_name in score_columns:
            detailed_scores[col_name] = student_data[col_name]

        data_to_return = {
            "name": student_data[name_col],
            "total_score": student_data[total_col],
            "details": detailed_scores
        }

        return (data_to_return, stats)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่าน Google Sheet: {e}")
        return (None, None)


# ================================================================
# 🔹 ฟังก์ชันสมัคร Slash Command /score (ดึงชื่อเล่นอัตโนมัติ)
# ================================================================
def register_score_command(bot: commands.Bot, guild: discord.Object):

    @bot.tree.command(
        name="score",
        description="ค้นหาคะแนนจากชื่อเล่น (8 ตัวแรกเป็นรหัสนักศึกษา)",
        guild=guild
    )
    async def score(interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            # 🔹 อ่านชื่อเล่น (nickname) ของผู้ใช้
            member = interaction.user
            guild_member = interaction.guild.get_member(member.id)
            nickname = guild_member.nick if guild_member and guild_member.nick else member.display_name

            # 🔹 ดึง 8 ตัวแรกของชื่อเล่นมาเป็น student_id
            student_id = nickname[:8]

            # ตรวจสอบว่าเป็นตัวเลข 8 หลักไหม
            if not (student_id.isdigit() and len(student_id) == 8):
                await interaction.followup.send(
                    f"❌ ไม่สามารถอ่านรหัสนักศึกษาจากชื่อเล่นของคุณได้\n"
                    f"กรุณาตั้งชื่อเล่นให้ขึ้นต้นด้วยรหัสนักศึกษา (เช่น `68071234Name`)\n\n"
                    f"**ชื่อเล่นปัจจุบัน:** `{nickname}`"
                )
                return

            # 🔹 โหลดข้อมูลจาก Google Sheet (run ใน thread แยก)
            loop = asyncio.get_running_loop()
            data, stats = await loop.run_in_executor(None, get_student_score, student_id)

            if data is None and stats is None:
                await interaction.followup.send(
                    "⚠️ เกิดข้อผิดพลาดในการอ่าน Google Sheet (ตรวจสอบสิทธิ์ Share หรือ GID)"
                )
                return

            if data is None:
                await interaction.followup.send(
                    f"❌ ไม่พบข้อมูลนักศึกษา ID: `{student_id}` (จากชื่อเล่น `{nickname}`)"
                )
                return

            student_name = data["name"]
            total_score = data["total_score"]

            # 🔹 สร้าง Embed แสดงผล
            embed = discord.Embed(
                title=f"📊 รายงานคะแนน: {student_name}",
                description=f"**จากชื่อเล่น:** {nickname}\n**ID ที่ตรวจพบ:** `{student_id}`",
                color=discord.Color.blue()
            )

            # แสดงคะแนนย่อย
            for score_name, score_value in data["details"].items():
                if "Unnamed" not in score_name:
                    embed.add_field(name=score_name, value=str(score_value), inline=True)

            # คะแนนรวม
            embed.add_field(name="-" * 30, value="", inline=False)
            embed.add_field(name="คะแนนรวม", value=f"**{total_score}**", inline=False)

            # 🔹 สถิติคะแนนรวม (Min/Max/Avg/SD)
            if stats:
                def format_stat(value):
                    try:
                        return f"{float(value):.2f}"
                    except (ValueError, TypeError):
                        return str(value)

                stat_line_1 = (
                    f"{stats['min_name']}: **{format_stat(stats['min_val'])}** | "
                    f"{stats['max_name']}: **{format_stat(stats['max_val'])}**"
                )
                stat_line_2 = (
                    f"{stats['avg_name']}: **{format_stat(stats['avg_val'])}** | "
                    f"{stats['sd_name']}: **{format_stat(stats['sd_val'])}**"
                )

                embed.add_field(
                    name="📈 สถิติคะแนนรวม (จากแถว 2 & 3)",
                    value=f"{stat_line_1}\n{stat_line_2}",
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /score: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}")

