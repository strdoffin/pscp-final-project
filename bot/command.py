from discord import app_commands
import discord

async def setup_commands(bot: discord.Client):
    @bot.tree.command(name="ping", description="say pong!")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("pong!")
    
    @bot.tree.command(name="PSCP", description="say PSCP!")
    async def pscp(interaction: discord.Interaction):
        await interaction.response.send_message("PSCP!")
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)