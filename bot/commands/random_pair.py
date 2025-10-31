import discord
import pandas as pd
import asyncio
import random
import csv
import io
from discord import app_commands
from discord.ext import commands

# --- Google Sheet settings ---
SHEET_ID = "1ydK3l7Lks3p57Tmvxrhk3dqu5dVcOmNgBetvVrWnNyk"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1740081435"
csv_path = "data/random_pairs.csv"

# --- Function: read data from Google Sheet ---
def fetch_student_list():
    """
    Read ID (col A), Name (col B), and Group (col C) from Google Sheet
    """
    try:
        df = pd.read_csv(SHEET_URL)

        # Assume: Column A=ID, B=Name, C=Group
        id_col = df.columns[0]
        name_col = df.columns[1]
        group_col = df.columns[2]

        # Clean and ensure valid data
        df = df.dropna(subset=[id_col, name_col])
        df[id_col] = df[id_col].astype(str)
        df[name_col] = df[name_col].astype(str)
        df[group_col] = df[group_col].astype(str)

        return df[[id_col, name_col, group_col]]

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่าน Google Sheet: {e}")
        return None


# --- Register /pair command ---
def register_random_command(bot: commands.Bot, guild: discord.Object):
    """
    Register slash command /pair for random pairing with group column
    """

    @bot.tree.command(name="random_pair", description="random pair save in csv", guild=guild)
    async def pair(interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            loop = asyncio.get_running_loop()
            df = await loop.run_in_executor(None, fetch_student_list)

            if df is None or df.empty:
                await interaction.followup.send("❌ ไม่สามารถดึงข้อมูลจาก Google Sheet ได้ครับ")
                return

            # Shuffle all rows
            shuffled = df.sample(frac=1).reset_index(drop=True)

            # Build pairs and keep Column C (Group)
            pairs = []
            for i in range(0, len(shuffled) - 1, 2):
                a = shuffled.iloc[i]
                b = shuffled.iloc[i + 1]
                group_value = a[2]  # Column C
                pairs.append((a[0], a[1], b[0], b[1], group_value))

            # If odd number of students
            if len(shuffled) % 2 != 0:
                last = shuffled.iloc[-1]
                pairs.append((last[0], last[1], "-", "ไม่มีคู่", last[2]))

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID1", "Name1", "ID2", "Name2", "Group"])
            for row in pairs:
                writer.writerow(row)
            output.seek(0)

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID1", "Name1", "ID2", "Name2", "Group"])
                for row in pairs:
                    writer.writerow(row)

            # Send the saved CSV file to Discord
            csv_file = discord.File(csv_path, filename="random_pairs.csv")
            await interaction.followup.send("✅ สุ่มจับคู่เสร็จแล้วครับ!", file=csv_file)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน command /pair: {e}")
            await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}")

    print("✅ 'pair' command registered.")
