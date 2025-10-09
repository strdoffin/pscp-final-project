import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from bot.commands.tong import register_tong
from bot.commands.ping import register_ping
from bot.commands.dmlink import register_dmlink

def run_bot():
    """Starting Discord Bot"""
    load_dotenv(dotenv_path=".env.local")

    token = os.getenv('DISCORD_TOKEN')
    guild_id = int(os.getenv('GUILD_ID'))

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    guild = discord.Object(id=guild_id)
    bot = commands.Bot(command_prefix='!', intents=intents)
    register_tong(bot, guild)
    register_ping(bot, guild)
    register_dmlink(bot, guild)

    @bot.event
    async def on_ready():
        print(f'✅ Logged in as {bot.user}')
        try:
            synced = await bot.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild_id}')
        except Exception as e:
            print("Error syncing commands:", e)


    bot.run(token, log_handler=handler, log_level=logging.DEBUG)

if __name__ == "__main__":
    run_bot()
