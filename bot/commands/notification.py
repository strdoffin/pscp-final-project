import discord
import datetime
from discord.ext import tasks
import pytz
from bot.commands import data_store

TARGET_CHANNEL_ID = 1425142738717904926
DAY_TZ = pytz.timezone("Asia/Bangkok")

def register_notification(client: discord.Client, guild: discord.Object):


    # Optional: fixed notifications if wanna add more...
    # SCHEDULES.append({
    #     "weekday": 0,
    #     "hour": 9,
    #     "minute": 0,
    #     "message": "🌞 Happy Monday everyone!"
    # })
    SCHEDULES = [
        {
            "weekday": 2,  # Wednesday
            "hour": 18,
            "minute": 30,
            "message": "📌 อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ\n@everyone"
        },
        {
            "weekday": 3,  # Thursday
            "hour": 21,
            "minute": 0,
            "message": "📌 อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ last chance\n@everyone"
        }
    ]
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

        # Check if any link has release today
        for item in links:
            if item["day"] == today_str and now.hour == 18 and now.minute == 30:
                await channel.send(f"🚀 Release today! Check this link: {item['link']} @everyone")

        for task in SCHEDULES:
            if (
                now.weekday() == task["weekday"]
                and now.hour == task["hour"]
                and now.minute == task["minute"]
            ):
                await channel.send(task["message"])

    return sent_noti
