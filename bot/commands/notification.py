import discord
import datetime
from discord.ext import tasks
import pytz
from bot.commands import data_store

TARGET_CHANNEL_ID = 1425142738717904926
DAY_TZ = pytz.timezone("Asia/Bangkok")

def register_notification(client: discord.Client, guild: discord.Object):

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

        # Optional: fixed notifications
        if now.weekday() == 2 and now.hour == 18 and now.minute == 30:
            await channel.send("📌 อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ\n@everyone")
        if now.weekday() == 3 and now.hour == 21 and now.minute == 0:
            await channel.send("📌 อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ last chance\n@everyone")

    return sent_noti
