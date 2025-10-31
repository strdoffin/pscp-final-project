# bot/commands/score.py
import discord
import pandas as pd
import asyncio
from discord import app_commands
from discord.ext import commands

# --- ส่วนดึงข้อมูลจาก Google Sheet ---

# URL ของ Google Sheet (เหมือนเดิม)
SHEET_ID = "1ydK3l7Lks3p57Tmvxrhk3dqu5dVcOmNgBetvVrWnNyk"
# บรรทัดที่ 12 (ใหม่)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=861657501"
# สมมติฐานโครงสร้างไฟล์ Excel:
# Col A (index 0): ID นักศึกษา
# Col B (index 1): ชื่อนามสกุล
# Col C-K (index 2-10): คะแนนย่อย
# Col L (index 11): คะแนนรวม

def get_student_score(student_id: str):
    """
    ดึงข้อมูลนักศึกษาจาก Google Sheet โดยใช้ ID (ทำงานแบบ blocking)
    """
    try:
        df = pd.read_csv(SHEET_URL)

        id_col = df.columns[0]
        name_col = df.columns[1]
        total_col = df.columns[11] 

        df[id_col] = df[id_col].astype(str)
        student_id = str(student_id)

        result_row = df[df[id_col] == student_id]

        if result_row.empty:
            return None

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
        
        return data_to_return

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่าน Google Sheet: {e}")
        return None

# --- ส่วนลงทะเบียนคำสั่งกับ Bot ---

def register_score_command(bot: commands.Bot, guild: discord.Object):
    """
    ฟังก์ชันสำหรับลงทะเบียนคำสั่ง /score ให้กับ bot
    """
    
    @bot.tree.command(name="score", description="ค้นหาคะแนนนักศึกษาจาก ID", guild=guild)
    @app_commands.describe(student_id="ID นักศึกษา 68070xxx")
    async def score(interaction: discord.Interaction, student_id: str):
        """
        Slash command /score ที่รับ ID นักศึกษา
        """
        try:
            # 1. แจ้งว่ากำลังทำงาน
            await interaction.response.defer()

            # 2. เรียกใช้ฟังก์ชัน get_student_score ใน thread แยก
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, get_student_score, student_id)

            # 3. ตรวจสอบผลลัพธ์
            if data is None:
                await interaction.followup.send(f"ไม่พบข้อมูลนักศึกษา ID: `{student_id}` ครับ")
                return

            # 4. สร้าง Embed เพื่อตอบกลับ
            student_name = data['name']
            total_score = data['total_score']
            
            embed = discord.Embed(
                title=f"📊 รายงานคะแนน: {student_name}",
                description=f"**ID:** {student_id}",
                color=discord.Color.blue()
            )

            # 5. เพิ่มคะแนนย่อย (จากคอลัมน์ C-K)
            for score_name, score_value in data['details'].items():
                if "Unnamed" not in score_name: # กันคอลัมน์ว่าง
                    embed.add_field(name=score_name, value=str(score_value), inline=True)
            
            # 6. เพิ่มคะแนนรวม (จากคอลัมน์ L)
            embed.add_field(name="-"*30, value="", inline=False) # เส้นคั่น
            embed.add_field(
                name="คะแนนรวม (Column L)", 
                value=f"**{total_score}**", 
                inline=False
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /score: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}")

    print("✅ 'score' command registered.")