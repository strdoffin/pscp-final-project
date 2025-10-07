import discord

def register_tong(client: discord.Client, guild: discord.Guild):

    @client.tree.command(name="tong", description="I Kwai TONG!", guild=guild)
    async def tong(interaction: discord.Interaction):
        await interaction.response.send_message("I Kwai TONG!")