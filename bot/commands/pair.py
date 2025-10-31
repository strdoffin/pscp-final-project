import os
import pandas as pd
import discord
from discord.ext import tasks
import datetime
import asyncio
import pytz  # for timezone

# --- Config ---
LOCAL_CSV = r"data\pair_data.csv"
GLOBAL_DF = None  # cache
THAI_TZ = pytz.timezone("Asia/Bangkok")  # Thailand timezone

# --- Load CSV once ---
def load_csv():
    global GLOBAL_DF
    if GLOBAL_DF is not None:
        return GLOBAL_DF

    if not os.path.exists(LOCAL_CSV):
        raise FileNotFoundError(f"CSV file not found: {LOCAL_CSV}")

    df = pd.read_csv(LOCAL_CSV)
    for col in ["Partner 1 (Name)", "Partner 1 (Username)",
                "Partner 2 (Name)", "Partner 2 (Username)", "Group"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    GLOBAL_DF = df
    print(f"✅ Loaded CSV: {LOCAL_CSV}")
    return df


# --- Find Pair ---
def find_pair(df, target):
    for _, row in df.iterrows():
        name1, user1 = row["Partner 1 (Name)"], row["Partner 1 (Username)"]
        name2, user2 = row["Partner 2 (Name)"], row["Partner 2 (Username)"]
        section = row["Group"]

        if target in [name1, user1, name2, user2, user1.replace("it",""), user2.replace("it","")]:
            return {
                "section": section,
                "p1_name": name1,
                "p1_user": user1,
                "p2_name": name2,
                "p2_user": user2
            }
    return None


# --- /pair command ---
def register_pair(bot: discord.Client, guild: discord.Object):
    df = load_csv()

    @bot.tree.command(name="pair", description="Check your PSCP weekly pair info", guild=guild)
    async def pair_cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        discord_name = interaction.user.display_name.strip()
        parts = [p.strip() for p in discord_name.split("|")]

        result = None
        for part in parts:
            result = find_pair(df, part)
            if result:
                break

        if result:
            msg = (
                f"👥 **Pair info for {discord_name}**\n"
                f"📘 Section: {result['section']}\n"
                f"- {result['p1_name']} ({result['p1_user']})\n"
                f"- {result['p2_name']} ({result['p2_user']})"
            )
        else:
            msg = f"❌ No pair found for **{discord_name}**"

        await interaction.followup.send(msg, ephemeral=True)

    print("✅ /pair command registered")


# --- DM sending ---
async def send_weekly_dm(bot):
    df = load_csv()

    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue

            display_name = member.display_name.strip()
            parts = [p.strip() for p in display_name.split("|")]

            found_pair = None
            for part in parts:
                found_pair = find_pair(df, part)
                if found_pair:
                    break

            if found_pair:
                msg = (
                    f"👥 **Weekly Pair Reminder!**\n"
                    f"📘 Section: {found_pair['section']}\n"
                    f"- {found_pair['p1_name']} ({found_pair['p1_user']})\n"
                    f"- {found_pair['p2_name']} ({found_pair['p2_user']})"
                )
                try:
                    await member.send(msg)
                    print(f"✅ Sent DM to {member.display_name}")
                except Exception as e:
                    print(f"⚠️ Failed to DM {member.display_name}: {e}")
            else:
                print(f"⚠️ No pair found for {display_name}")


async def weekly_dm_scheduler(bot):
    while True:
        now = datetime.datetime.now(THAI_TZ)

        # Calculate next Friday 08:42
        days_ahead = 4 - now.weekday()  # Friday == 4
        if days_ahead < 0 or (days_ahead == 0 and (now.hour > 8 or (now.hour == 8 and now.minute >= 42))):
            days_ahead += 7
        next_friday = datetime.datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=8,
            minute=42,
            second=0,
            tzinfo=THAI_TZ
        ) + datetime.timedelta(days=days_ahead)

        delay = (next_friday - now).total_seconds()
        print(f"⏰ Next weekly DM scheduled at {next_friday}")
        await asyncio.sleep(delay)

        # Send DMs
        await send_weekly_dm(bot)
        print("✅ Weekly DMs sent!")

# --- /dmpair command for testing ---
def register_dmpair(bot: discord.Client, guild: discord.Object):
    @bot.tree.command(name="dmpair", description="Send test pair info via DM", guild=guild)
    async def dmpair_cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await send_weekly_dm(interaction.client)
        await interaction.followup.send("✅ Sent test DM! (check your inbox)", ephemeral=True)
