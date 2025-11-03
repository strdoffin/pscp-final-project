import pytest

from bot import import_complete
from bot.main import run_bot

def test_import_complete(capsys):
    import_complete()
    captured = capsys.readouterr()
    assert "Imported Success" in captured.out

def test_run_bot_exists():
    assert callable(run_bot)