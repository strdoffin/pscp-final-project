import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from bot.commands.tong import register_tong
from bot.commands.notification import register_notification
from bot.commands.pair import register_pair, register_dmpair, weekly_dm_scheduler  # import scheduler
from bot.commands.notification import register_notification
from bot.commands.feedback_link import register_feedback_link

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
    register_feedback_link(bot, guild)
    register_tong(bot, guild)
    register_notification(bot, guild)
    register_pair(bot, guild)
    register_dmpair(bot, guild)

    send_noti_task = register_notification(bot,guild)

    @bot.event
    async def on_ready():
        print(f'✅ Logged in as {bot.user}')

        # Start the weekly scheduler if not already running
        if not hasattr(bot, 'weekly_dm_started'):
            bot.loop.create_task(weekly_dm_scheduler(bot))
            bot.weekly_dm_started = True
            print("🚀 Weekly DM scheduler started")

        if not send_noti_task.is_running():
            send_noti_task.start()
            print("Daily notification task started.")

        # Sync commands
        try:
            synced = await bot.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild_id}')
        except Exception as e:
            print("Error syncing commands:", e)

    bot.run(token, log_handler=handler, log_level=logging.DEBUG)


if __name__ == "__main__":
    run_bot()
