import pytest
from discord.ext import commands
from bot.commands.ijudge import register_ijudge_link
from bot.commands.feedback import register_feedback_schedule
from bot.commands.pair import register_pair, register_dmpair
from bot.commands.score import register_score_command
from bot.commands.random_pair import register_random_command
from bot.commands.jsontools import register_json_tools
from bot.commands.help import register_help_command
from bot.commands.setup import register_setup_command
from bot.commands.notification import register_notification

@pytest.fixture
def mock_bot():
    bot = commands.Bot(command_prefix="!", intents=None)
    yield bot

def test_register_all_commands(mock_bot):
    guild = None
    register_ijudge_link(mock_bot, guild)
    register_feedback_schedule(mock_bot, guild)
    register_pair(mock_bot, guild)
    register_dmpair(mock_bot)
    register_score_command(mock_bot, guild)
    register_random_command(mock_bot, guild)
    register_json_tools(mock_bot, guild)
    register_help_command(mock_bot, guild)
    register_setup_command(mock_bot, guild)
    send_noti_task = register_notification(mock_bot, guild)

    # Get all slash commands
    tree_commands = [c.name for c in mock_bot.tree.get_commands()]
    # print(tree_commands)  # For debugging

    # Assert the real command names
    expected_commands = [
        "addijudge",
        "addfeedback",
        "pair",
        "dmpair",
        "score",
        "random_pair",
        "help",
        "setup",
    ]
    print("\n")
    for i,cmd_name in enumerate(expected_commands):
        assert cmd_name in tree_commands, f"Command {cmd_name} not registered"
        print(f"✅ Command {i + 1} '{cmd_name}' checked")

    assert send_noti_task is not None
    print(f"✅ Notification checked")

