import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os


def run_bot():
    load_dotenv(dotenv_path=".env.local")

    token = os.getenv('DISCORD_TOKEN')
    handler = logging.FileHandler(
        filename='discord.log', encoding='utf-8', mode='w')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"We are ready to go in {bot.user.name}")

	#find everyone in discord
    # @bot.event
    # async def on_ready():
    #     print(f"Logged in as {bot.user}")
    #     for guild in bot.guilds:
    #         print(f"Server: {guild.name}")
    #         async for member in guild.fetch_members(limit=None):
    #             nickname = member.nick if member.nick else "(no nickname)"
    #             print(
    #                 f"Username: {member.name}, Nickname: {nickname}, ID: {member.id}")

    @bot.event
    async def on_member_join(member):
        # DM to member
        await member.send(f"Welcome {member.name} to server")

    @bot.event
    async def on_message(message):
        # handle infinite loop
        if message.author == bot.user:
            return
        if "pscp" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} คำต้องห้ามนะ")
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)


if __name__ == "__main__":
    run_bot()
