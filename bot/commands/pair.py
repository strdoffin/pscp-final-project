import os
import asyncio
import datetime
import pandas as pd
import discord
from discord.ext import tasks
import pytz  # For timezone handling

# --- Config ---
LOCAL_CSV = r"data/random_pairs.csv"
GLOBAL_DF = None  # Cache for loaded CSV
THAI_TZ = pytz.timezone("Asia/Bangkok")  # Thailand timezone

# --- Load CSV ---
def load_csv():
    """Load and cache the CSV file containing pairing data."""

    if not os.path.exists(LOCAL_CSV):
        raise FileNotFoundError(f"CSV file not found: {LOCAL_CSV}")

    df = pd.read_csv(LOCAL_CSV)
    for col in [
        "Partner 1 (Name)",
        "Partner 1 (Username)",
        "Partner 2 (Name)",
        "Partner 2 (Username)",
        "Group",
    ]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # print(f"✅ Loaded CSV: {LOCAL_CSV}")
    return df


# --- Find Pair ---
def find_pair(df: pd.DataFrame, target: str):
    """Find pairing info for a given name or username."""
    for _, row in df.iterrows():
        name1, user1 = row["Partner 1 (Name)"], row["Partner 1 (Username)"]
        name2, user2 = row["Partner 2 (Name)"], row["Partner 2 (Username)"]
        section = row["Group"]

        if target in [
            name1,
            user1,
            name2,
            user2,
            user1.replace("it", ""),
            user2.replace("it", ""),
        ]:
            return {
                "section": section,
                "p1_name": name1,
                "p1_user": user1,
                "p2_name": name2,
                "p2_user": user2,
            }
    return None


# --- /pair command ---
def register_pair(bot: discord.Client, guild: discord.Object):
    """Register the /pair command to check pair info."""

    @bot.tree.command(
        name="pair",
        description="Check your PSCP weekly pair info",
        guild=guild,
    )
    async def pair_cmd(interaction: discord.Interaction):
        df = load_csv()
        await interaction.response.defer(ephemeral=True)

        discord_name = interaction.user.display_name.strip()
        parts = [p.strip() for p in discord_name.split("|")]

        result = None
        for part in parts:
            result = find_pair(df, part)
            if result:
                break

        if result:
            embed = discord.Embed(
                title=f"👥 **Pair info for {discord_name}**",
                description=f"📘 Section: {result['section']}",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Partner 1",
                value=f"```{result['p1_name']} ({result['p1_user']})```",
                inline=False,
            )
            embed.add_field(
                name="Partner 2",
                value=f"```{result['p2_name']} ({result['p2_user']})```",
                inline=False,
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="👥 **Pair information**",
                description=f"❌ No pair found for **{discord_name}**",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    # print("✅ /pair command registered")


# --- DM Sending ---
async def send_weekly_dm(bot: discord.Client):
    """Send weekly pair info via DM to all guild members."""
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
                embed = discord.Embed(
                    title="👥 **Weekly Pair Reminder!**",
                    description=f"📘 Section: {found_pair['section']}",
                    color=discord.Color.blue(),
                )
                embed.add_field(
                    name="Partner 1",
                    value=f"```{found_pair['p1_name']} "
                    f"({found_pair['p1_user']})```",
                    inline=False,
                )
                embed.add_field(
                    name="Partner 2",
                    value=f"```{found_pair['p2_name']} "
                    f"({found_pair['p2_user']})```",
                    inline=False,
                )

                try:
                    await member.send(embed=embed)
                    print(f"✅ Sent DM to {member.display_name}")
                except Exception as e:
                    print(f"⚠️ Failed to DM {member.display_name}: {e}")
            else:
                print(f"⚠️ No pair found for {display_name}")


# --- Weekly Scheduler ---
async def weekly_dm_scheduler(bot: discord.Client):
    """Schedule weekly DM sending every Friday at 08:42 (Thai time)."""
    while True:
        now = datetime.datetime.now(THAI_TZ)

        # Calculate next Friday at 08:42
        days_ahead = 4 - now.weekday()  # Friday == 4
        if days_ahead < 0 or (
            days_ahead == 0 and (now.hour > 8 or (now.hour == 8 and now.minute >= 42))
        ):
            days_ahead += 7

        next_friday = datetime.datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=8,
            minute=42,
            second=0,
            tzinfo=THAI_TZ,
        ) + datetime.timedelta(days=days_ahead)

        delay = (next_friday - now).total_seconds()
        # print(f"⏰ Next weekly DM scheduled at {next_friday}")
        await asyncio.sleep(delay)

        # Send DMs
        await send_weekly_dm(bot)
        print("✅ Weekly DMs sent!")


def register_dmpair(bot: discord.Client):
    """Register the /dmpair command for any guild, with timeout/error handling."""

    @bot.tree.command(
        name="dmpair",
        description="Send pair info via DM to members of this guild",
    )
    
    async def dmpair_cmd(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น", ephemeral=True
            )
            return
        if not any(role.name == "TA" for role in interaction.user.roles):
            await interaction.response.send_message(
            "❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (เฉพาะ TA เท่านั้น)",
            ephemeral=True,
        )
            return
        await interaction.response.defer(ephemeral=True)
        df = load_csv()
        guild = interaction.guild

        try:
            # ใช้ asyncio.wait_for เพื่อจำกัดเวลาการทำงานไม่เกิน 30 วินาที
            await asyncio.wait_for(send_dm_to_guild(guild, df), timeout=30)
            await interaction.followup.send(
                "✅ ส่ง DM เสร็จสิ้น! (check your inbox)", ephemeral=True
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "❌ ไม่สามารถใช้คำสั่งนี้ได้ (Timeout)", ephemeral=True
            )
        except Exception as e:
            print(f"⚠️ Error in /dmpair: {e}")
            await interaction.followup.send(
                "❌ ไม่สามารถใช้คำสั่งนี้ได้", ephemeral=True
            )


async def send_dm_to_guild(guild, df):
    """Send pair DM to all members of a guild."""
    async for member in guild.fetch_members(limit=None):
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
            embed = discord.Embed(
                title="👥 **Weekly Pair Info**",
                description=f"📘 Section: {found_pair['section']}",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Partner 1",
                value=f"```{found_pair['p1_name']} ({found_pair['p1_user']})```",
                inline=False,
            )
            embed.add_field(
                name="Partner 2",
                value=f"```{found_pair['p2_name']} ({found_pair['p2_user']})```",
                inline=False,
            )

            try:
                await member.send(embed=embed)
                print(f"✅ Sent DM to {member.display_name}")
            except Exception as e:
                print(f"⚠️ Failed to DM {member.display_name}: {e}")
