import discord
import datetime
from discord.ext import tasks
import pandas
import pytz  # for timezone

target_channel_id = 1425142738717904926
day_tz = pytz.timezone("Asia/Bangkok")

def register_dmlink(client: discord.Client, guild: discord.Guild):

    @tasks.loop(minutes=1)
    async def sent_noti():
        day = datetime.datetime.now(day_tz)
        await client.wait_until_ready()
        channel = client.get_channel(target_channel_id)
        if day.weekday() == 2 and day.hour==18 and day.minute==30:
            await channel.send("อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ\n@everyone")
        if day.weekday() == 3 and day.hour==21 and day.minute==0:
            await channel.send("อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ last chance\n@everyone")
        else:
            print("error")

    @client.event
    async def on_ready():
        if not sent_noti.is_running():
            sent_noti.start()
            print("Daily notification task started.")

    client.run("MTQyMTc0OTI5MjYxOTY2MTQxMg.GNdr3Y.vpXdi3PtB3YXenorrp1Idxx0hzv19K3nwlumhY")