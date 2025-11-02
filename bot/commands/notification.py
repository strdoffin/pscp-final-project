"""notifications"""
from datetime import datetime
import discord
from discord.ext import tasks
import pytz
from bot.commands import data_store

TARGET_CHANNEL_ID = 1425142738717904926
DAY_TZ = pytz.timezone("Asia/Bangkok")


def register_notification(client: discord.Client, guild: discord.Object):
    """Register periodic iJudge and feedback deadline notifications."""
    sent_notifications = set()

    @tasks.loop(minutes=1)
    async def sent_noti():
        await client.wait_until_ready()
        now = datetime.now(DAY_TZ)
        channel = client.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            return

        async def process_items(items, label: str):
            """Iterate through each scheduled item and send reminders."""
            for item in items:
                try:
                    # Build datetime from separate fields
                    item_dt = datetime(
                        year=item["year"],
                        month=item["month"],
                        day=item["day"],
                        hour=item["hour"],
                        minute=item["minute"]
                    )
                    item_dt = DAY_TZ.localize(item_dt)
                    delta = item_dt - now

                    # Create unique reminder keys
                    base = (
                        f"{item.get('round', item.get('message', ''))}_"
                        f"{item['year']:04d}-{item['month']:02d}-"
                        f"{item['day']:02d} {item['hour']:02d}:"
                        f"{item['minute']:02d}"
                    )
                    keys = {
                        "3d": f"{base}_3d",
                        "1d": f"{base}_1d",
                        "1h": f"{base}_1h",
                        "30m": f"{base}_30m",
                    }

                    async def send(msg: str, key: str):
                        if key not in sent_notifications:
                            await channel.send(msg)
                            sent_notifications.add(key)

                    dt_str = (
                        f"{item['year']:04d}-{item['month']:02d}-"
                        f"{item['day']:02d} {item['hour']:02d}:"
                        f"{item['minute']:02d}"
                    )

                    total_sec = delta.total_seconds()

                    if 3 * 86400 - 60 <= total_sec <= 3 * 86400 + 60:
                        await send(
                            f"📢 @everyone เหลืออีก **3 วัน** ก่อน "
                            f"`{item.get('round', item.get('message', ''))}` "
                            f"({label})!\n🕒 {dt_str}",
                            keys["3d"],
                        )
                    elif 86400 - 60 <= total_sec <= 86400 + 60:
                        await send(
                            f"⚠️ @everyone เหลืออีก **1 วันสุดท้าย** ก่อน "
                            f"`{item.get('round', item.get('message', ''))}` "
                            f"({label})!\n📅 {dt_str}",
                            keys["1d"],
                        )
                    elif 3600 - 60 <= total_sec <= 3600 + 60:
                        await send(
                            f"⏰ @everyone อีก **1 ชั่วโมง** จะถึง "
                            f"`{item.get('round', item.get('message', ''))}` "
                            f"({label})!\n📅 {dt_str}",
                            keys["1h"],
                        )
                    elif 1800 - 60 <= total_sec <= 1800 + 60:
                        await send(
                            f"🚨 @everyone เหลือ **30 นาทีสุดท้าย** ก่อน "
                            f"`{item.get('round', item.get('message', ''))}` "
                            f"({label})!\n📅 {dt_str}",
                            keys["30m"],
                        )

                except Exception as e:
                    print(f"⚠️ Error checking {label} item: {e}")

        await process_items(data_store.load_links(), "iJudge")
        await process_items(data_store.load_schedules(), "Feedback")

    return sent_noti
