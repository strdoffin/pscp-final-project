import discord
import datetime
from discord.ext import tasks
import pandas
import pytz  # for timezone

target_channel_id = 1425142738717904926 #channel id
day_tz = pytz.timezone("Asia/Bangkok") #set timezone

def register_notification(client: discord.Client, guild: discord.Guild):

    @tasks.loop(minutes=1) #check every 1 min
    async def sent_noti():
        day = datetime.datetime.now(day_tz)
        await client.wait_until_ready()
        channel = client.get_channel(target_channel_id)
        if day.weekday() == 2 and day.hour==18 and day.minute==30: # วันพุธ 6 โมงครึ่ง
            await channel.send("อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ\n@everyone")
        if day.weekday() == 3 and day.hour==21: # วันพฤหัส 3 ทุ่ม
            await channel.send("อย่าลืมทำ Feedback PSCP นะครับเพิ่ลๆ last chance\n@everyone")
        else:
            print("Time checked, no message needed.")
    return sent_noti
