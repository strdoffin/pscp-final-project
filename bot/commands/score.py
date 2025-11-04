"""/score + /setscore"""
import discord
import pandas as pd
import asyncio
from discord.ext import commands
from discord import app_commands
import json
import os

SHEET_ID = ""
SHEET_URL = ""
CONFIG_FILE = "data/sheet_config.json"

def save_sheet_config():
    global SHEET_ID, SHEET_URL
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"SHEET_ID": SHEET_ID, "SHEET_URL": SHEET_URL}, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ เก็บค่า Sheet ไม่สำเร็จ: {e}")
        return False

def load_sheet_config():
    global SHEET_ID, SHEET_URL
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                SHEET_ID = data.get("SHEET_ID", SHEET_ID)
                SHEET_URL = data.get("SHEET_URL", SHEET_URL)
                print(f"📄 โหลด Sheet config สำเร็จ: {SHEET_URL}")
        except Exception as e:
            print(f"❌ โหลด Sheet config ล้มเหลว: {e}")

def set_sheet_config_from_url(sheet_url: str):
    global SHEET_ID, SHEET_URL
    try:
        if "export?format=csv" in sheet_url:
            SHEET_URL = sheet_url
            parts = sheet_url.split("/")
            SHEET_ID = parts[5] if len(parts) > 5 else SHEET_ID
        elif "/edit" in sheet_url:
            parts = sheet_url.split("/")
            SHEET_ID = parts[5]
            gid = 0
            if "gid=" in sheet_url:
                gid_part = sheet_url.split("gid=")[1]
                gid_str = "".join(c for c in gid_part if c.isdigit())
                if gid_str:
                    gid = int(gid_str)
            SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        else:
            SHEET_URL = sheet_url

        # บันทึกลงไฟล์ทันที
        save_sheet_config()

        return True, f"✅ ตั้งค่า Sheet ใหม่สำเร็จ\nURL: {SHEET_URL}"
    except Exception as e:
        return False, f"❌ เกิดข้อผิดพลาด: {e}"


def get_student_score(student_id: str):
    try:
        df = pd.read_csv(SHEET_URL, header=0)

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

        id_col = df.columns[0]
        name_col = df.columns[1]
        total_col = df.columns[11]

        df[id_col] = df[id_col].astype(str)
        student_id = str(student_id)

        student_df = df.iloc[2:].copy()
        student_df[id_col] = student_df[id_col].astype(str)

        result_row = student_df[student_df[id_col] == student_id]

        if result_row.empty:
            return (None, stats)

        student_data = result_row.iloc[0]

        score_columns = df.columns[2:11]
        detailed_scores = {}
        for col_name in score_columns:
            val = student_data[col_name]
            detailed_scores[col_name] = val if pd.notna(val) else "ไม่พบ"

        total_score = student_data[total_col]
        total_score = total_score if pd.notna(total_score) else "ไม่พบ"

        data_to_return = {
            "name": student_data[name_col] if pd.notna(student_data[name_col]) else "ไม่พบ",
            "total_score": total_score,
            "details": detailed_scores
        }

        return (data_to_return, stats)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่าน Google Sheet: {e}")
        return (None, None)


def register_score_command(bot: commands.Bot, guild: discord.Object):

    @bot.tree.command(
        name="score",
        description="ค้นหาคะแนนจากชื่อเล่น (8 ตัวแรกเป็นรหัสนักศึกษา)",
        guild=guild
    )
    async def score(interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            member = interaction.user
            guild_member = interaction.guild.get_member(member.id)
            nickname = guild_member.nick if guild_member and guild_member.nick else member.display_name

            student_id = nickname[:8]

            if not (student_id.isdigit() and len(student_id) == 8):
                await interaction.followup.send(
                    f"❌ ไม่สามารถอ่านรหัสนักศึกษาจากชื่อเล่นของคุณได้\n"
                    f"กรุณาตั้งชื่อเล่นให้ขึ้นต้นด้วยรหัสนักศึกษา (เช่น `68071234Name`)\n\n"
                    f"**ชื่อเล่นปัจจุบัน:** `{nickname}`"
                )
                return

            loop = asyncio.get_running_loop()
            data, stats = await loop.run_in_executor(None, get_student_score, student_id)

            if data is None and stats is None:
                await interaction.followup.send("⚠️ เกิดข้อผิดพลาดในการอ่าน Google Sheet")
                return

            if data is None:
                await interaction.followup.send(
                    f"❌ ไม่พบข้อมูลนักศึกษา ID: `{student_id}` (จากชื่อเล่น `{nickname}`)"
                )
                return

            student_name = data["name"]
            total_score = data["total_score"]

            embed = discord.Embed(
                title=f"📊 รายงานคะแนน: {student_name}",
                description=f"**รหัสนักศึกษา:** {nickname}\n",
                color=discord.Color.blue()
            )

            for score_name, score_value in data["details"].items():
                if "Unnamed" not in score_name:
                    embed.add_field(
                        name=score_name, 
                        value=str(score_value), 
                        inline=True
                    )

            embed.add_field(name="-" * 30, value="", inline=False)
            embed.add_field(name="คะแนนรวม", value=f"**{total_score}**", inline=False)

            if stats:
                def format_stat(value):
                    try:
                        return f"{float(value):.2f}"
                    except (ValueError, TypeError):
                        return str(value) if pd.notna(value) else "ไม่พบ"

                stat_line_1 = (
                    f"{stats['min_name']}: **{format_stat(stats['min_val'])}** | "
                    f"{stats['max_name']}: **{format_stat(stats['max_val'])}**"
                )
                stat_line_2 = (
                    f"{stats['avg_name']}: **{format_stat(stats['avg_val'])}** | "
                    f"{stats['sd_name']}: **{format_stat(stats['sd_val'])}**"
                )

                embed.add_field(
                    name="📈 สถิติคะแนนรวม",
                    value=f"{stat_line_1}\n{stat_line_2}",
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /score: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}")

def register_setscore_command(bot: commands.Bot, guild: discord.Object):

    @bot.tree.command(
        name="setscore",
        description="ตั้งค่า Google Sheet ใหม่ โดยใส่ลิงก์ export CSV",
        guild=guild
    )
    @app_commands.describe(sheet_url="ใส่ลิงก์ Google Sheet แบบ export CSV หรือ edit")
    async def setscore(interaction: discord.Interaction, sheet_url: str):
        try:
            if not any(role.name == "TA" for role in interaction.user.roles):
                await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)
            success, message = set_sheet_config_from_url(sheet_url)
            await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /setscore: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)
