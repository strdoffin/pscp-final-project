"""/score + /setscore"""
import discord
import pandas as pd
import asyncio
from discord.ext import commands
from discord import app_commands
import json
import os

# --- ค่าคงที่และตัวแปร Global ---
SHEET_ID = ""
SHEET_URL = ""
CONFIG_FILE = "data/sheet_config.json"

# --- [แก้ไข] ตรวจสอบและสร้าง Directory 'data' ถ้ายังไม่มี ---
DATA_DIR = os.path.dirname(CONFIG_FILE)
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        print(f"📁 สร้างโฟลเดอร์ {DATA_DIR} สำหรับเก็บ config")
    except Exception as e:
        print(f"❌ ไม่สามารถสร้างโฟลเดอร์ {DATA_DIR}: {e}")
# ---------------------------------------------------------

def save_sheet_config():
    """บันทึก Sheet ID และ URL ลงในไฟล์ JSON"""
    global SHEET_ID, SHEET_URL
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"SHEET_ID": SHEET_ID, "SHEET_URL": SHEET_URL}, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ เก็บค่า Sheet ไม่สำเร็จ: {e}")
        return False

def load_sheet_config():
    """โหลด Sheet ID และ URL จากไฟล์ JSON เมื่อบอทเริ่มทำงาน"""
    global SHEET_ID, SHEET_URL
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                SHEET_ID = data.get("SHEET_ID", SHEET_ID)
                SHEET_URL = data.get("SHEET_URL", SHEET_URL)
                if SHEET_URL:
                    print(f"📄 โหลด Sheet config สำเร็จ: {SHEET_URL}")
                else:
                    print("📄 โหลด Sheet config แล้ว แต่ยังไม่มี URL (รอ /setscore)")
        except Exception as e:
            print(f"❌ โหลด Sheet config ล้มเหลว: {e}")
    else:
        print(f"ℹ️ ไม่พบไฟล์ config ({CONFIG_FILE}), รอการตั้งค่าผ่าน /setscore")

def set_sheet_config_from_url(sheet_url: str):
    """แปลง URL (edit หรือ csv) และบันทึกลง config"""
    global SHEET_ID, SHEET_URL
    try:
        if "export?format=csv" in sheet_url:
            # ใช้ URL ที่ให้มาโดยตรง
            SHEET_URL = sheet_url
            parts = sheet_url.split("/")
            SHEET_ID = parts[5] if len(parts) > 5 else SHEET_ID
        elif "/edit" in sheet_url:
            # แปลง URL แบบ /edit ให้เป็น /export
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
            # ถ้าเป็นรูปแบบอื่นที่ไม่รู้จัก ให้ใช้ตามที่ส่งมา
            SHEET_URL = sheet_url

        # บันทึกลงไฟล์ทันที
        save_sheet_config()

        return True, f"✅ ตั้งค่า Sheet ใหม่สำเร็จ\nURL: {SHEET_URL}"
    except Exception as e:
        return False, f"❌ เกิดข้อผิดพลาดในการแปลง URL: {e}"

# --- [แก้ไข] เรียกใช้ฟังก์ชัน load_sheet_config() ทันที ---
load_sheet_config()
# -------------------------------------------------------

def get_student_score(student_id: str):
    """
    ดึงข้อมูลคะแนนนักศึกษาและสถิติจาก Google Sheet
    """
    try:
        # ตรวจสอบว่ามี URL หรือยัง
        if not SHEET_URL:
            print("❌ ไม่สามารถดึงคะแนนได้: ยังไม่ได้ตั้งค่า SHEET_URL")
            return (None, "No URL") # คืนค่า None, และ "No URL" เพื่อแจ้งข้อผิดพลาด

        df = pd.read_csv(SHEET_URL, header=0)

        # 1. อ่านสถิติ โดยใช้ชื่อคอลัมน์แทนตำแหน่ง
        try:
            lower_cols = [col.strip().lower() for col in df.columns]

            def get_col(name):
                for i, col in enumerate(lower_cols):
                    if name in col:  # เช่น 'min', 'max', 'avg', 'sd'
                        return df.columns[i]
                return None

            col_min = get_col("min")
            col_max = get_col("max")
            col_avg = get_col("avg")
            col_sd  = get_col("sd")

            if all([col_min, col_max, col_avg, col_sd]):
                stats = {
                    "min_name": "ต่ำสุด",
                    "max_name": "สูงสุด",
                    "avg_name": "เฉลี่ย",
                    "sd_name": "ส่วนเบี่ยงเบน",

                    "min_val": df[col_min].dropna().iloc[0],
                    "max_val": df[col_max].dropna().iloc[0],
                    "avg_val": df[col_avg].dropna().iloc[0],
                    "sd_val":  df[col_sd].dropna().iloc[0],
                }
            else:
                stats = None
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการอ่านสถิติจากชื่อคอลัมน์: {e}")
            stats = None


        # 2. ตั้งชื่อคอลัมน์หลัก
        id_col = df.columns[0]
        name_col = df.columns[1]
        total_col = df.columns[11] # คอลัมน์ L

        # 3. เตรียม DataFrame สำหรับค้นหาข้อมูลนักศึกษา
        df[id_col] = df[id_col].astype(str)
        student_id = str(student_id)

        # ค้นหาข้อมูลนักศึกษา (เริ่มตั้งแต่แถวที่ 3 ของ Sheet, หรือ index 2 ของ df)
        student_df = df.iloc[2:].copy()
        student_df[id_col] = student_df[id_col].astype(str)

        result_row = student_df[student_df[id_col] == student_id]

        if result_row.empty:
            return (None, stats) # ไม่พบนักศึกษา แต่คืนสถิติไป (ถ้ามี)

        # 4. ดึงข้อมูลนักศึกษาที่พบ
        student_data = result_row.iloc[0]

        # 5. ดึงคะแนนย่อย (คอลัมน์ C ถึง K หรือ 2-10)
        score_columns = df.columns[2:11]
        detailed_scores = {}
        for col_name in score_columns:
            val = student_data[col_name]
            detailed_scores[col_name] = val if pd.notna(val) else "ไม่พบ" # 0 หรือ "ไม่พบ" ก็ได้

        # 6. ดึงคะแนนรวม
        total_score = student_data[total_col]
        total_score = total_score if pd.notna(total_score) else "ไม่พบ"

        data_to_return = {
            "name": student_data[name_col] if pd.notna(student_data[name_col]) else "ไม่พบ",
            "total_score": total_score,
            "details": detailed_scores
        }

        return (data_to_return, stats)

    except pd.errors.EmptyDataError:
        print(f"❌ เกิดข้อผิดพลาด: Google Sheet ที่ {SHEET_URL} ไม่มีข้อมูล")
        return (None, None)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่าน Google Sheet: {e}")
        return (None, None)


def register_score_command(bot: commands.Bot, guild: discord.Object):
    """
    ลงทะเบียนคำสั่ง /score
    """
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

            # เรียกใช้ฟังก์ชัน get_student_score
            loop = asyncio.get_running_loop()
            data, stats = await loop.run_in_executor(None, get_student_score, student_id)

            # --- จัดการ Error Case ต่างๆ ---
            if stats == "No URL":
                await interaction.followup.send("⚠️ ยังไม่ได้ตั้งค่า Google Sheet ครับ กรุณาติดต่อ TA")
                return

            if data is None and stats is None:
                await interaction.followup.send(f"⚠️ เกิดข้อผิดพลาดในการอ่าน Google Sheet ({SHEET_URL})")
                return

            if data is None:
                await interaction.followup.send(
                    f"❌ ไม่พบข้อมูลนักศึกษา ID: `{student_id}` (จากชื่อเล่น `{nickname}`)"
                )
                return
            # -------------------------------

            student_name = data["name"]
            total_score = data["total_score"]

            embed = discord.Embed(
                title=f"📊 รายงานคะแนน: {student_name}",
                description=f"**รหัสนักศึกษา:** {student_id}\n(จากชื่อ `{nickname}`)",
                color=discord.Color.blue()
            )

            # เพิ่มคะแนนย่อย
            for score_name, score_value in data["details"].items():
                if "Unnamed" not in str(score_name): # กันคอลัมน์ที่ไม่มีชื่อ
                    embed.add_field(
                        name=score_name, 
                        value=str(score_value), 
                        inline=True
                    )
            
            # จัดรูปแบบให้สวยงาม (ถ้าคะแนนย่อยมี 9 ช่อง จะได้ขึ้น 3 แถวพอดี)
            # ถ้ามี 8 ช่อง อาจจะต้องเพิ่ม field ว่าง
            # if len(data["details"]) % 3 != 0:
            #     embed.add_field(name="\u200b", value="\u200b", inline=True)

            embed.add_field(name="-" * 30, value="", inline=False)
            embed.add_field(name="คะแนนรวม", value=f"**{total_score}**", inline=False)

            # เพิ่มสถิติ (ถ้ามี)
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
                    name="📈 สถิติคะแนนรวม (ทั้งห้อง)",
                    value=f"{stat_line_1}\n{stat_line_2}",
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /score: {e}")
            try:
                await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}")
            except discord.errors.InteractionResponded:
                pass


def register_setscore_command(bot: commands.Bot, guild: discord.Object):
    """
    ลงทะเบียนคำสั่ง /setscore (สำหรับ TA)
    """
    @bot.tree.command(
        name="setscore",
        description="[TA] ตั้งค่า Google Sheet ใหม่ โดยใส่ลิงก์ export CSV หรือ edit",
        guild=guild
    )
    @app_commands.describe(sheet_url="ใส่ลิงก์ Google Sheet แบบ export CSV หรือ edit")
    async def setscore(interaction: discord.Interaction, sheet_url: str):
        try:
            # ตรวจสอบ Role (แก้ชื่อ Role ได้ตามต้องการ)
            if not any(role.name == "TA" for role in interaction.user.roles):
                await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่งนี้ (เฉพาะ TA)", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)
            success, message = set_sheet_config_from_url(sheet_url)
            await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /setscore: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)
