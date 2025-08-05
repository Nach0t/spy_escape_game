# spy_escape_game.py

import pygame
import sys
import heapq
import random

# === CONFIGURACIÓN ===
TILE_SIZE = 40
GRID_WIDTH = 10
GRID_HEIGHT = 10
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 5

# === COLORES ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 150)

# === GENERADOR DE MAPA CONECTADO ===
def generate_connected_map():
    while True:
        grid = [[1 if x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1 else random.choice([0, 1, 0]) for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]

        player_pos = (1, 1)
        goal_pos = (GRID_WIDTH - 2, GRID_HEIGHT - 2)
        guard_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

        grid[player_pos[1]][player_pos[0]] = 2  # Espía
        grid[goal_pos[1]][goal_pos[0]] = 3      # Meta
        grid[guard_pos[1]][guard_pos[0]] = 0    # Limpia para colocación de guardia

        temp_pg = Playground(grid)
        path = temp_pg.a_star(player_pos, goal_pos)
        if path and temp_pg.is_valid(*guard_pos):
            grid[guard_pos[1]][guard_pos[0]] = 4  # Guardia
            return grid

# === CLASE DEL ENTORNO ===
class Playground:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]
        self.player_pos = self.find_position(2)
        self.goal_pos = self.find_position(3)
        self.guard_pos = self.find_position(4)
        self.path = []
        self.guard_timer = 0

    def find_position(self, value):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == value:
                    return (x, y)
        return None

    def is_valid(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and self.grid[y][x] in [0, 3]

    def neighbors(self, x, y):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                yield (nx, ny)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, goal):
        open_set = [(0 + self.heuristic(start, goal), 0, start, [])]
        visited = set()

        while open_set:
            est_total, cost, current, path = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)
            new_path = path + [current]
            if current == goal:
                return new_path[1:]
            for neighbor in self.neighbors(*current):
                if neighbor not in visited:
                    heapq.heappush(open_set, (cost + 1 + self.heuristic(neighbor, goal), cost + 1, neighbor, new_path))
        return []

    def move_along_path(self):
        if self.path:
            new_x, new_y = self.path.pop(0)
            old_x, old_y = self.player_pos
            self.grid[old_y][old_x] = 0
            self.grid[new_y][new_x] = 2
            self.player_pos = (new_x, new_y)

    def move_guard_randomly(self):
        self.guard_timer += 1
        if self.guard_timer < 5:
            return
        self.guard_timer = 0
        gx, gy = self.guard_pos
        possible_moves = list(self.neighbors(gx, gy))
        if possible_moves:
            new_x, new_y = random.choice(possible_moves)
            self.grid[gy][gx] = 0
            self.grid[new_y][new_x] = 4
            self.guard_pos = (new_x, new_y)

    def is_win(self):
        return self.player_pos == self.goal_pos

    def is_caught(self):
        px, py = self.player_pos
        gx, gy = self.guard_pos
        vision = [(gx + dx, gy + dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]]
        return (px, py) in vision

    def get_guard_vision(self):
        gx, gy = self.guard_pos
        return [(gx + dx, gy + dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)] if 0 <= gx + dx < GRID_WIDTH and 0 <= gy + dy < GRID_HEIGHT and self.grid[gy + dy][gx + dx] != 1]

# === FUNCIONES AUXILIARES ===
def draw_grid(screen, playground):
    gx, gy = playground.guard_pos
    vision = playground.get_guard_vision()

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = playground.grid[y][x]

            if tile == 1:
                color = GRAY
            elif tile == 2:
                color = BLUE
            elif tile == 3:
                color = GREEN
            elif tile == 4:
                color = RED
            elif (x, y) in vision:
                color = LIGHT_YELLOW
            else:
                color = WHITE

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

# === MAIN LOOP ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    random_map = generate_connected_map()
    playground = Playground(random_map)
    running = True

    while running:
        screen.fill(BLACK)
        draw_grid(screen, playground)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                if playground.is_valid(grid_x, grid_y):
                    playground.path = playground.a_star(playground.player_pos, (grid_x, grid_y))

        playground.move_along_path()
        playground.move_guard_randomly()

        if playground.is_win():
            print("¡Ganaste! Llegaste a la sala de control.")
            running = False

        if playground.is_caught():
            print("¡Te vio el guardia! Fin del juego.")
            running = False

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
