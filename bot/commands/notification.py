import discord
from discord.ext import tasks
from datetime import datetime
import pytz
from bot.commands import data_store

TARGET_CHANNEL_ID = 1425142738717904926
DAY_TZ = pytz.timezone("Asia/Bangkok")

def register_notification(client: discord.Client, guild: discord.Object):
    sent_notifications = set()

    @tasks.loop(minutes=1)
    async def sent_noti():
        await client.wait_until_ready()
        now = datetime.now(DAY_TZ)
        channel = client.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            return

        async def process_items(items, label: str):
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
                    # Localize to Bangkok timezone
                    item_dt = DAY_TZ.localize(item_dt)
                    delta = item_dt - now

                    # Create unique keys for each reminder
                    keys = {
                        "3d": f"{item.get('round', item.get('message', ''))}_{item['year']:04d}-{item['month']:02d}-{item['day']:02d} {item['hour']:02d}:{item['minute']:02d}_3d",
                        "1d": f"{item.get('round', item.get('message', ''))}_{item['year']:04d}-{item['month']:02d}-{item['day']:02d} {item['hour']:02d}:{item['minute']:02d}_1d",
                        "1h": f"{item.get('round', item.get('message', ''))}_{item['year']:04d}-{item['month']:02d}-{item['day']:02d} {item['hour']:02d}:{item['minute']:02d}_1h",
                        "30m": f"{item.get('round', item.get('message', ''))}_{item['year']:04d}-{item['month']:02d}-{item['day']:02d} {item['hour']:02d}:{item['minute']:02d}_30m",
                    }

                    async def send(msg, key):
                        if key not in sent_notifications:
                            await channel.send(msg)
                            sent_notifications.add(key)

                    dt_str = f"{item['year']:04d}-{item['month']:02d}-{item['day']:02d} {item['hour']:02d}:{item['minute']:02d}"

                    if 3*86400 - 60 <= delta.total_seconds() <= 3*86400 + 60:
                        await send(f"📢 @everyone เหลืออีก **3 วัน** ก่อน `{item.get('round', item.get('message', ''))}` ({label})!\n🕒 {dt_str}", keys["3d"])
                    elif 86400 - 60 <= delta.total_seconds() <= 86400 + 60:
                        await send(f"⚠️ @everyone เหลืออีก **1 วันสุดท้าย** ก่อน `{item.get('round', item.get('message', ''))}` ({label})!\n📅 {dt_str}", keys["1d"])
                    elif 3600 - 60 <= delta.total_seconds() <= 3600 + 60:
                        await send(f"⏰ @everyone อีก **1 ชั่วโมง** จะถึง `{item.get('round', item.get('message', ''))}` ({label})!\n📅 {dt_str}", keys["1h"])
                    elif 1800 - 60 <= delta.total_seconds() <= 1800 + 60:
                        await send(f"🚨 @everyone เหลือ **30 นาทีสุดท้าย** ก่อน `{item.get('round', item.get('message', ''))}` ({label})!\n📅 {dt_str}", keys["30m"])

                except Exception as e:
                    print(f"⚠️ Error checking {label} item: {e}")

        await process_items(data_store.load_links(), "iJudge")
        await process_items(data_store.load_schedules(), "Feedback")

    return sent_noti
