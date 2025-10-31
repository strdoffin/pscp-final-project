import discord
from discord import app_commands

def register_test_commands(client: discord.Client, guild: discord.Object, noti_task):
    """
    Registers /testnoti command to manually trigger the notification loop.
    Works for both iJudge and feedback schedules.
    """
    @client.tree.command(
        name="testnoti",
        description="Manually test notification logic",
        guild=guild
    )
    async def testnoti_command(interaction: discord.Interaction):
        await interaction.response.send_message("🔧 Running notification test now...", ephemeral=True)
        try:
            # Call the notification loop once
            await noti_task()
            await interaction.followup.send("✅ Test notification completed (if conditions matched).", ephemeral=True)
        except Exception as e:
            # Catch errors to prevent bot crash
            await interaction.followup.send(f"❌ Error running test notification: {e}", ephemeral=True)
