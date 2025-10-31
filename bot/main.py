import discord
from discord.ext import commands
import logging
from bot.commands.feedback import register_feedback_schedule
from bot.commands.tong import register_tong
from bot.commands.notification import register_notification
from bot.commands.pair import register_pair, register_dmpair, weekly_dm_scheduler
from bot.commands.notification import register_notification
from bot.commands.ijudge import register_ijudge_link
from bot.commands.score import register_score_command  # ⬇️ 1. เพิ่ม import นี้
from bot.commands.random_pair import register_random_command
from bot.commands.ijudge import register_ijudge_link
from bot.commands.test_command import register_test_commands
from bot.commands.jsontools import register_json_tools

from dotenv import load_dotenv
import os

def run_bot():
    """Starting Discord Bot"""
    load_dotenv(dotenv_path=".env.local")

    token = os.getenv('DISCORD_TOKEN')
    guild_id = int(os.getenv('GUILD_ID'))

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True 

    guild = discord.Object(id=guild_id)
    bot = commands.Bot(command_prefix='!', intents=intents)

    # ✅ Register all commands
    register_ijudge_link(bot, guild)
    register_feedback_schedule(bot, guild)
    register_tong(bot, guild)
    register_pair(bot, guild)
    register_dmpair(bot, guild)
    register_score_command(bot, guild) # ⬇️ 2. เพิ่มการ register คำสั่งนี้
    register_random_command(bot, guild)

    send_noti_task = register_notification(bot,guild)
    register_json_tools(bot, guild)

    @bot.event
    async def on_ready():
        print(f'✅ Logged in as {bot.user}')

        # Start the notification loop inside on_ready (async context)
        if not send_noti_task.is_running():
            send_noti_task.start()
            print("Daily notification task started.")

        # Start the weekly DM scheduler
        if not hasattr(bot, 'weekly_dm_started'):
            bot.loop.create_task(weekly_dm_scheduler(bot))
            bot.weekly_dm_started = True
            print("🚀 Weekly DM scheduler started")

        # Sync commands
        try:
            synced = await bot.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild_id}')
        except Exception as e:
            print("Error syncing commands:", e)

    bot.run(token, log_handler=handler, log_level=logging.DEBUG)


if __name__ == "__main__":
    run_bot()