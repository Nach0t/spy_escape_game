# test_game.py
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import spy_escape_game  # ← corregido

def test_game_import():
    assert True

def test_generate_map():
    grid = spy_escape_game.generate_connected_map()
    assert isinstance(grid, list)
    assert any(2 in row for row in grid)
    assert any(3 in row for row in grid)
    assert any(4 in row for row in grid)
