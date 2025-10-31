import discord
import datetime
from discord.ext import tasks
import pytz
from bot.commands import data_store

TARGET_CHANNEL_ID = 1425142738717904926
DAY_TZ = pytz.timezone("Asia/Bangkok")

def register_notification(client: discord.Client, guild: discord.Object):
    sent_notifications = set()
    @tasks.loop(minutes=1)
    async def sent_noti():
        await client.wait_until_ready()
        now = datetime.datetime.now(DAY_TZ)
        today_str = now.strftime("%Y-%m-%d")
        channel = client.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            return

        # Load saved links
        links = data_store.load_links()

        # Check if ijudge has release today
        for item in links:
            if item["day"] == today_str and now.hour == 18 and now.minute == 30:
                await channel.send(f"🚀 Release today! Check this link: {item['link']} @everyone")

        schedules = data_store.load_schedules()

        for task in schedules:
            # Convert task date & hour/minute to datetime object
            task_dt = datetime.datetime.strptime(
                f"{task['datetime']} {task['hour']:02d}:{task['minute']:02d}",
                "%Y-%m-%d %H:%M"
            )
            task_dt = DAY_TZ.localize(task_dt)
            # Calculate difference from now
            delta = task_dt - now

            # Prepare keys for different reminders
            keys = {
                "exact": f"{task['datetime']}_{task['hour']:02d}{task['minute']:02d}_exact",
                "1_day": f"{task['datetime']}_{task['hour']:02d}{task['minute']:02d}_1day",
                "3_days": f"{task['datetime']}_{task['hour']:02d}{task['minute']:02d}_3days",
                "1_hour": f"{task['datetime']}_{task['hour']:02d}{task['minute']:02d}_1hour",
            }

            # Send reminders
            if 0 < delta.total_seconds() <= 3600 and keys["1_hour"] not in sent_notifications:
                await channel.send(f"⏰ @everyone ใกล้หมดเวลาส่ง feedback form แล้วนะ: {task['message'].replace('\\n', '\n')}")
                sent_notifications.add(keys["1_hour"])
            elif 86400 - 60 <= delta.total_seconds() <= 86400 + 60 and keys["1_day"] not in sent_notifications:
                await channel.send(f"⏰ @everyone อย่าลืมส่ง feedback form กันนะเหลืออีก1วัน: {task['message'].replace('\\n', '\n')}")
                sent_notifications.add(keys["1_day"])
            elif 3*86400 - 60 <= delta.total_seconds() <= 3*86400 + 60 and keys["3_days"] not in sent_notifications:
                await channel.send(f"⏰ @everyone อย่าลืมส่ง feedback form กันนะเหลืออีก3วัน: {task['message'].replace('\\n', '\n')}")
                sent_notifications.add(keys["3_days"])

    return sent_noti
