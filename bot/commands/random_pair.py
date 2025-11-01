import discord
import pandas as pd
import asyncio
import random
import csv
import io
from discord.ext import commands

# --- Google Sheet settings ---
SHEET_ID = "1ydK3l7Lks3p57Tmvxrhk3dqu5dVcOmNgBetvVrWnNyk"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1740081435"
csv_path = "data/random_pairs.csv"

# สำหรับเปลี่ยน Column ข้อมูล
COLUMN_MAPPING = {
    "USERNAME": 0,  # B
    "FULLNAME": 1,  # C
    "SEC": 2,        # H
}

# --- Function: read data from Google Sheet ---


def fetch_student_list():
    """
    Read ID (col A), Name (col B), and Group (col C) from Google Sheet
    """

    try:
        all_students = []
        df = pd.read_csv(SHEET_URL)
        data = df.dropna().values.tolist()

        for row in data[1:]:  # ข้าม header
            username = str(row[COLUMN_MAPPING["USERNAME"]])
            fullname = str(row[COLUMN_MAPPING["FULLNAME"]])
            sec = int(row[COLUMN_MAPPING["SEC"]])

            if username and not pd.isna(sec):
                all_students.append({
                    "username": username,
                    "fullname": fullname,
                    "sec": sec
                })
        return all_students
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่าน Google Sheet: {e}")
        return None

# --- แบ่งกลุ่มตาม section ---


def group_students(students, sections):
    """
    แบ่งรายชื่อออกเป็นตามกลุ่ม
    """

    groups = dict([(g, []) for g in sections])

    for s in students:
        if str(s['sec']) in groups.keys():
            groups.get(str(s['sec'])).append(s)

    return groups


# --- สุ่มจับคู่ภายในกลุ่ม ---
def pair_students_in_group(student_group, group_name):
    """
    สุ่มจับคู่ Pair ตาม Section
    """
    random.shuffle(student_group)
    pairs = []

    for i in range(0, len(student_group), 2):
        a = student_group[i]
        if i + 1 < len(student_group):
            b = student_group[i + 1]
            pairs.append([
                group_name,
                a["fullname"], a["username"], a["sec"],
                b["fullname"], b["username"], b["sec"]
            ])
        else:
            pairs.append([
                group_name,
                a["fullname"], a["username"], a["sec"],
                "UNPAIRED", "UNPAIRED", ""
            ])
    return pairs


# --- รวมและบันทึก CSV ---


def generate_pair_csv():
    """
    ฟังชั่นสำหรับ สุ่มคู่ Pair และ บันทึก CSV
    """
    students = fetch_student_list()
    if not students:
        raise ValueError("ไม่พบข้อมูลนักเรียนในชีตที่กำหนด")

    sections = set()

    for student in students:
        sections.add(str(student["sec"]))

    groups = group_students(students, sections)

    all_pairs = []

    for section in sorted(sections):
        all_pairs += pair_students_in_group(
            groups[section], "Section " + section)

    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "Group",
        "Partner 1 (Username)", "Partner 1 (Name)", "Partner 1 (Sec)",
        "Partner 2 (Username)", "Partner 2 (Name)", "Partner 2 (Sec)",
    ]
    writer.writerow(headers)
    writer.writerows(all_pairs)
    output.seek(0)

    # Save to file
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_pairs)

    return csv_path

# --- Register /pair command ---


def register_random_command(bot: commands.Bot, guild: discord.Object):
    """
    Register slash command /pair for random pairing with group column
    """

    @bot.tree.command(name="random_pair", description="random pair save in csv", guild=guild)
    async def pair(interaction: discord.Interaction):
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message("❌ ไม่มีสิทธิ์ในการใช้คำสั่ง", ephemeral=True)
            return
        try:
            await interaction.response.defer()
            loop = asyncio.get_running_loop()
            file_path = await loop.run_in_executor(None, generate_pair_csv)

            file = discord.File(file_path, filename="random_pairs.csv")
            await interaction.followup.send("✅ สุ่มจับคู่เสร็จสมบูรณ์! ตรวจสอบไฟล์ CSV ด้านล่างครับ", file=file , ephemeral=True)
        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /pair: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)
        print("✅ 'pair' command registered.")
