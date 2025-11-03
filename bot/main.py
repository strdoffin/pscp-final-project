"""main function"""
import discord
from discord.ext import commands
import logging
from bot.commands.feedback import register_feedback_schedule
from bot.commands.notification import register_notification
from bot.commands.pair import register_pair, register_dmpair, weekly_dm_scheduler
from bot.commands.ijudge import register_ijudge_link
from bot.commands.score import register_score_command
from bot.commands.random_pair import register_random_command
from bot.commands.setup import register_setup_command
from bot.commands.test_command import register_test_commands
from bot.commands.jsontools import register_json_tools
from bot.commands.help import register_help_command

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


    @bot.event
    async def on_ready():
        print(f'✅ Logged in as {bot.user}')
        print(r"""
 ____  ____   ____ ____    ___ ____     ___  _   _ _     ___ _   _ _____
|  _ \/ ___| / ___|  _ \  |_ _/ ___|   / _ \| \ | | |   |_ _| \ | | ____|
| |_) \___ \| |   | |_) |  | |\___ \  | | | |  \| | |    | ||  \| |  _|
|  __/ ___) | |___|  __/   | | ___) | | |_| | |\  | |___ | || |\  | |___
|_|   |____/ \____|_|     |___|____/   \___/|_| \_|_____|___|_| \_|_____|
""")
        # Sync commands
        try:
            bot.tree.clear_commands(guild=None)
            await bot.tree.sync(guild=None)
            # ✅ Register all commands
            register_ijudge_link(bot, guild)
            register_feedback_schedule(bot, guild)
            register_pair(bot, guild)
            register_dmpair(bot)
            register_score_command(bot, guild)
            register_random_command(bot, guild)
            register_json_tools(bot, guild)
            register_help_command(bot, guild)
            register_setup_command(bot, guild)
            send_noti_task = register_notification(bot, guild)
            synced = await bot.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands')
            for cmd in synced:
                print(f" - /{cmd.name} #{cmd.description}")
        except Exception as e:
            print("Error syncing commands:", e)
                # Start the notification loop inside on_ready (async context)
        if not send_noti_task.is_running():
            send_noti_task.start()
            # print("Daily notification task started.")

        # Start the weekly DM scheduler (now per guild)
        if not hasattr(bot, 'weekly_dm_started'):
            bot.loop.create_task(weekly_dm_scheduler(bot))
            bot.weekly_dm_started = True
            # print("🚀 Weekly DM scheduler started")

    bot.run(token, log_handler=handler, log_level=logging.DEBUG)


if __name__ == "__main__":
    run_bot()
