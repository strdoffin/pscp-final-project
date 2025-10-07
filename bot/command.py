from discord import app_commands
import discord

async def setup_commands(bot: discord.Client):
    @bot.tree.command(name="PSCP", description="say PSCP!")
    async def pscp(interaction: discord.Interaction):
        await interaction.response.send_message("PSCP!")
    @bot.tree.command(name="TONG", description="I Kwai TONG!")
    async def pscp(interaction: discord.Interaction):
        await interaction.response.send_message("I Kwai TONG!")
    @bot.tree.command(name="ping", description="say pong!")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("pong!")