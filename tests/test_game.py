# test_game.py

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"  # evita abrir ventana

import pytest
import pygame
import spy_escape_game

def test_game_import():
    assert True  # Si importar no lanza error, la prueba pasa

def test_generate_map():
    grid = spy_escape_game.generate_connected_map()
    assert isinstance(grid, list)
    assert any(2 in row for row in grid)  # tiene espía
    assert any(3 in row for row in grid)  # tiene meta
    assert any(4 in row for row in grid)  # tiene guardia
