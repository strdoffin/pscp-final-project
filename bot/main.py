import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os


class Client(commands.Bot):
    async def on_ready(self):
        print(f'✅ Logged in as {self.user}')
        guild_id = int(os.getenv('GUILD_ID'))
        guild = discord.Object(id=guild_id)

        try:
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild_id}')
        except Exception as e:
            print("Error syncing commands:", e)



def run_bot():
    """Starting Discord Bot"""
    load_dotenv(dotenv_path=".env.local")

    token = os.getenv('DISCORD_TOKEN')
    guild_id = int(os.getenv('GUILD_ID'))

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    client = Client(command_prefix='!', intents=intents)
    guild = discord.Object(id=guild_id)

    @client.tree.command(name="pscps", description="Say PSCP!", guild=guild)
    async def pscp(interaction: discord.Interaction):
        await interaction.response.send_message("PSCP!")
    @client.tree.command(name="tong", description="I Kwai TONG!", guild=guild)
    async def tong(interaction: discord.Interaction):
        await interaction.response.send_message("I Kwai TONG!")
    @client.tree.command(name="katang", description="I Kwaii katang!", guild=guild)
    async def tong(interaction: discord.Interaction):
        await interaction.response.send_message("I Kwaii katang!")

    client.run(token, log_handler=handler, log_level=logging.DEBUG)

<<<<<<< HEAD
=======

>>>>>>> 0dccc806fdf14e60575677eb0ece16cb267a1e7a
if __name__ == "__main__":
    run_bot()
