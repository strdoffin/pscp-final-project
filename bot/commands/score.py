"""/score"""
import discord
import pandas as pd
import asyncio
from discord import app_commands
from discord.ext import commands

SHEET_ID = "1ydK3l7Lks3p57Tmvxrhk3dqu5dVcOmNgBetvVrWnNyk"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=861657501"

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


def register_score_command(bot: commands.Bot, guild: discord.Object):
    
    @bot.tree.command(name="score", description="ค้นหาคะแนนนักศึกษาจาก ID", guild=guild)
    @app_commands.describe(student_id="ID นักศึกษา 68070xxx")
    async def score(interaction: discord.Interaction, student_id: str):
        try:
            await interaction.response.defer(ephemeral=True)

            loop = asyncio.get_running_loop()
            data, stats = await loop.run_in_executor(None, get_student_score, student_id)

            if data is None and stats is None:
                await interaction.followup.send(f"เกิดข้อผิดพลาดในการอ่าน Google Sheet ครับ (อาจต้องเช็คสิทธิ์ Share หรือ GID)")
                return

            if data is None:
                await interaction.followup.send(f"ไม่พบข้อมูลนักศึกษา ID: `{student_id}` ครับ")
                return

            student_name = data['name']
            total_score = data['total_score']
            
            embed = discord.Embed(
                title=f"📊 รายงานคะแนน: {student_name}",
                description=f"**ID:** {student_id}",
                color=discord.Color.blue()
            )

            for score_name, score_value in data['details'].items():
                if "Unnamed" not in score_name:
                    embed.add_field(name=score_name, value=str(score_value), inline=True)
            
            embed.add_field(name="-"*30, value="", inline=False) 
            embed.add_field(
                name="คะแนนรวม", 
                value=f"**{total_score}**", 
                inline=False
            )

            if stats:
                try:
                    def format_stat(value):
                        try:
                            return f"{float(value):.2f}"
                        except (ValueError, TypeError):
                            return str(value) 

                    stat_line_1 = f"{stats['min_name']}: **{format_stat(stats['min_val'])}** | {stats['max_name']}: **{format_stat(stats['max_val'])}**"
                    stat_line_2 = f"{stats['avg_name']}: **{format_stat(stats['avg_val'])}** | {stats['sd_name']}: **{format_stat(stats['sd_val'])}**"
                    
                    embed.add_field(
                        name="📊 สถิติคะแนนรวม (จากแถว 2 & 3)",
                        value=f"{stat_line_1}\n{stat_line_2}",
                        inline=False
                    )
                except Exception as e:
                    print(f"เกิดข้อผิดพลาดในการจัดรูปแบบสถิติ: {e}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /score: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}")

    # print("✅ /core command registered.")