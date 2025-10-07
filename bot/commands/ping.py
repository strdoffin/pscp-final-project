import discord

def register_ping(client: discord.Client, guild: discord.Guild):

    @client.tree.command(name="ping", description="pong!", guild=guild)
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("pong!")