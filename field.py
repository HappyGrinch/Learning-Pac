import pygame
import time
from settings import (
    GRID_COLS, GRID_ROWS,
    LIGHT_GRAY, WALL_COLOR, WHITE, BLACK
)

def create_grid(width, height):
    cell_width = width / GRID_COLS
    cell_height = height / GRID_ROWS
    grid = {}
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            cell_id = row * GRID_COLS + col
            x = int(col * cell_width)
            y = int(row * cell_height)
            w = int(cell_width)
            h = int(cell_height)
            rect = pygame.Rect(x, y, w, h)
            grid[(row, col)] = {
                "id": cell_id,
                "rect": rect,
                "visit_count": 0,
                "last_visit": None,
                "last_decrement": None
            }
    return grid


def create_bunker(top_left, size, opening_side, opening_width):
    """
    Erzeugt nur den RAND eines Bunkers als Wandzellen (20x20 mit 4-Grid-Öffnung).
    """
    bunker_walls = set()
    start_row, start_col = top_left
    end_row = start_row + size - 1
    end_col = start_col + size - 1
    
    # Äußerer Rand als Wand
    for row in range(start_row, start_row + size):
        for col in range(start_col, start_col + size):
            if row == start_row or row == end_row or col == start_col or col == end_col:
                bunker_walls.add((row, col))
    
    # Öffnung zentriert entfernen (dort soll es frei sein)
    opening_start = start_col + (size - opening_width) // 2
    if opening_side == "top":
        for c in range(opening_start, opening_start + opening_width):
            bunker_walls.discard((start_row, c))
    elif opening_side == "bottom":
        for c in range(opening_start, opening_start + opening_width):
            bunker_walls.discard((end_row, c))
    
    return bunker_walls

def draw_full_grid_with_lines(screen, grid):
    # Definiere Farbwerte für Besuchsstufen:
    visit_colors = {
        1: (255, 230, 230),
        2: (255, 204, 204),
        3: (255, 178, 178),
        4: (255, 153, 153),
        5: (255, 128, 128)
    }
    for pos, cell_data in grid.items():
        rect = cell_data["rect"]
        # Wenn das Feld besucht wurde, fülle es mit dem entsprechenden Rosa; ansonsten weiß.
        if cell_data["visit_count"] > 0:
            level = min(cell_data["visit_count"], 5)
            pygame.draw.rect(screen, visit_colors[level], rect)
        else:
            pygame.draw.rect(screen, WHITE, rect)
        # Zeichne die Gitterlinie
        pygame.draw.rect(screen, (230,230,230), rect, 1)

def overpaint_walls(screen, grid, walls):
    """
    Übermalt alle Wandzellen mit etwas größerem Rechteck, um Grid-Linien sicher zu verdecken.
    Du kannst den inflate(...) -Wert anpassen, wenn an den Rändern noch Linien zu sehen sind.
    """
    for (row, col) in walls:
        if (row, col) in grid:
            # Originalrechteck der Zelle
            rect = grid[(row, col)]["rect"]
            # Leicht vergrößern, damit die darunterliegenden Linien verdeckt werden
            bigger_rect = rect.inflate(2, 2)
            pygame.draw.rect(screen, WALL_COLOR, bigger_rect)

def draw_hovered_cell(screen, grid, mouse_pos, font):
    """
    Hebt die Zelle hervor, über der sich die Maus befindet,
    und zeigt den eindeutigen Identifier dieser Zelle an.
    """
    for cell in grid.values():
        if cell["rect"].collidepoint(mouse_pos):
            pygame.draw.rect(screen, (200, 200, 200), cell["rect"])
            text_surface = font.render(str(cell["id"]), True, BLACK)
            text_rect = text_surface.get_rect(center=cell["rect"].center)
            screen.blit(text_surface, text_rect)
            break
def draw_house_marker(screen, grid, house_pos):
    cell_rect = grid[house_pos]["rect"]
    pygame.draw.rect(screen, (0, 0, 255), cell_rect)
    top_center = (cell_rect.centerx, cell_rect.top)
    bottom_left = (cell_rect.left, cell_rect.centery)
    bottom_right = (cell_rect.right, cell_rect.centery)
    pygame.draw.polygon(screen, (255, 0, 0), [top_center, bottom_left, bottom_right])

def update_cell_visits(grid, speed_factor):
    current_time = time.time()
    for pos, cell in grid.items():
        if cell["visit_count"] > 0 and cell["last_visit"] is not None:
            # Wenn das Feld länger als 60/speed_factor nicht betreten wurde:
            if current_time - cell["last_visit"] >= 60 / speed_factor:
                if cell["last_decrement"] is None:
                    cell["last_decrement"] = cell["last_visit"] + 60 / speed_factor
                # Solange 30/speed_factor Sekunden seit dem letzten Abbau vergangen sind:
                while current_time - cell["last_decrement"] >= 30 / speed_factor and cell["visit_count"] > 0:
                    cell["visit_count"] -= 1
                    cell["last_decrement"] += 30 / speed_factor
