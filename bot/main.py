import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from discord import app_commands


class Client(commands.Bot):
    async def on_ready(self):
        """Starting Discord Bot"""
        print(f'We have logged in as {self.user}')
        try:
            guild = discord.Object(id=int(os.getenv('GUILD_ID')))
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print("error syncing", e)

    async def on_message(self, message):
        if message.author == self.user:
            return


def run_bot():
    """Starting Discord Bot"""
    load_dotenv(dotenv_path=".env.local")

    token = os.getenv('DISCORD_TOKEN')
    handler = logging.FileHandler(
        filename='discord.log', encoding='utf-8', mode='w')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = Client(command_prefix='!', intents=intents)

    GUILD_ID = discord.Object(id=int(os.getenv('GUILD_ID')))

    @client.tree.command(name="pscps", description="say PSCP!", guild=GUILD_ID)
    async def pscp(interaction: discord.Interaction):
        await interaction.response.send_message("PSCP!")

    client.run(token, log_handler=handler, log_level=logging.DEBUG)


if __name__ == "__main__":
    run_bot()
