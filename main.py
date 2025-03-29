import pygame
import sys
import time
from settings import FPS, WHITE, GRID_COLS, GRID_ROWS
from field import (
    create_grid, create_bunker,
    draw_full_grid_with_lines, overpaint_walls, draw_hovered_cell, draw_house_marker, update_cell_visits
)
from character import PacManAgent
from mines import generate_mines, draw_mines, explosion_animation, play_explosion_sound
from food import generate_flowers, draw_flowers, eating_animation, play_eating_sound



# Einfacher Slider für die Spielgeschwindigkeit
class Slider:
    def __init__(self, x, y, width, height, min_val=1, max_val=10, initial=1):
        # Die internen Koordinaten des Sliders (relativ zum Overlay)
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.knob_radius = height // 2
        self.knob_x = self.value_to_pos(self.value)
        self.dragging = False
        # Offset, um absolute Bildschirmkoordinaten zu berechnen
        self.offset = (0, 0)

    def value_to_pos(self, value):
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(ratio * self.rect.width)

    def pos_to_value(self, pos):
        ratio = (pos - self.rect.x) / self.rect.width
        value = self.min_val + ratio * (self.max_val - self.min_val)
        return max(self.min_val, min(self.max_val, int(round(value))))

    def handle_event(self, event):
        # Wir passen die event.pos an, indem wir den Offset abziehen,
        # sodass die Koordinaten relativ zum Overlay sind.
        if hasattr(event, 'pos'):
            rel_pos = (event.pos[0] - self.offset[0], event.pos[1] - self.offset[1])
        else:
            rel_pos = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if rel_pos and self.get_knob_rect().collidepoint(rel_pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and rel_pos:
                self.value = self.pos_to_value(rel_pos[0])
                self.knob_x = self.value_to_pos(self.value)

    def get_knob_rect(self):
        return pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius, self.knob_radius * 2, self.knob_radius * 2)

    def draw(self, surface, font):
        # Zeichne die Schiene
        pygame.draw.line(surface, (200, 200, 200), (self.rect.x, self.rect.centery),
                         (self.rect.x + self.rect.width, self.rect.centery), 4)
        # Zeichne den Knopf
        pygame.draw.circle(surface, (100, 100, 100), (self.knob_x, self.rect.centery), self.knob_radius)
        # Zeichne den Text (Geschwindigkeit)
        text_surface = font.render(f"Speed: {self.value}", True, (255, 255, 255))
        surface.blit(text_surface, (self.rect.x, self.rect.y - text_surface.get_height() - 2))

def draw_overlay(screen, pacman, font, width, record_generation, record_survival, slider):
    overlay_width = 300
    overlay_height = 110  # Für zusätzlichen Text und den Slider
    overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
    overlay_surface.set_alpha(160)
    overlay_surface.fill((0, 0, 0))
    current_time = time.time()
    
    # Berechne verbleibende Lebenszeit in echten Sekunden:
    time_left = 20 - (current_time - pacman.last_food_time)
    if time_left < 0:
        time_left = 0

    intelligence = pacman.get_intelligence()
    
    text_str = (f"Gen: {pacman.generation} | Time left: {int(time_left)}s\n"
                f"Intelligence: {intelligence}\n"
                f"Record: Gen {record_generation} survived {int(record_survival)}s")
    lines = text_str.split("\n")
    y_offset = 5
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        overlay_surface.blit(text_surface, (10, y_offset))
        y_offset += text_surface.get_height() + 2

    # Setze den Offset für den Slider (Overlay-Position)
    slider.offset = ((width - overlay_width) // 2, 10)
    slider.draw(overlay_surface, font)
    
    x_pos = (width - overlay_width) // 2
    y_pos = 10
    screen.blit(overlay_surface, (x_pos, y_pos))
def main():
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    pygame.display.set_caption("Pac-Man Survival with Elite Learning and Speed Slider")
    clock = pygame.time.Clock()

    grid = create_grid(width, height)
    bunker_size = 20
    opening_width = 4
    top_left_bunker = create_bunker((0,0), bunker_size, "bottom", opening_width)
    top_right_bunker = create_bunker((0, GRID_COLS - bunker_size), bunker_size, "bottom", opening_width)
    bottom_left_bunker = create_bunker((GRID_ROWS - bunker_size, 0), bunker_size, "top", opening_width)
    bottom_right_bunker = create_bunker((GRID_ROWS - bunker_size, GRID_COLS - bunker_size), bunker_size, "top", opening_width)
    walls = top_left_bunker.union(top_right_bunker, bottom_left_bunker, bottom_right_bunker)
    house_pos = (GRID_ROWS // 2, GRID_COLS // 2)
    cell_size = int(width / GRID_COLS)
    pacman = PacManAgent(house_pos, cell_size, generation=1)

    obstacles = set()
    food_positions = set()

    initial_mines = generate_mines(grid, walls, house_pos, 100)
    initial_flowers = generate_flowers(grid, walls, house_pos, initial_mines, 150)
    current_mines = set(initial_mines)
    current_flowers = set(initial_flowers)

    font = pygame.font.SysFont(None, 24)

    # Recordvariablen
    record_generation = 0
    record_survival = 0

    no_improvement_counter = 0

    generation_data = []
    # Slider für Spielgeschwindigkeit (innerhalb des Overlays)
    slider = Slider(10, 70, 280, 20, min_val=1, max_val=10, initial=1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            slider.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if pacman.alive:
            pacman.update(grid, obstacles, food_positions, speed_factor=slider.value)

            current_time = time.time()
            # Aktualisiere das aktuell betretene Feld:
            cell = grid[pacman.pos]
            cell["visit_count"] = min(5, cell["visit_count"] + 1)
            cell["last_visit"] = current_time
            cell["last_decrement"] = None

            # Kollision mit Minen
            if pacman.pos in current_mines:
                play_explosion_sound()
                explosion_animation(screen, grid, pacman.pos)
                current_mines.remove(pacman.pos)
                pacman.alive = False
            if pacman.pos in walls:
                pacman.alive = False    
            # Kollision mit Blumen (Nahrung)
            if pacman.pos in current_flowers:
                play_eating_sound()
                eating_animation(screen, grid, pacman.pos, pacman)
                # Lebenszeit um 10 echte Sekunden verlängern:
                pacman.last_food_time += 10  
                pacman.reinforce(0.2)
                current_flowers.remove(pacman.pos)
        else:
                # Pac-Man ist gestorben – speichere seine Performance
            generation_data.append((pacman.survival_time, pacman.move_weights.copy()))
            if pacman.survival_time > record_survival:
                record_survival = pacman.survival_time
                record_generation = pacman.generation
                no_improvement_counter = 0  # Verbesserung -> Zähler zurücksetzen
            else:
                no_improvement_counter += 1

            pacman.generation += 1

            if len(generation_data) >= 3:
                elite = sorted(generation_data, key=lambda x: x[0], reverse=True)[:3]
                new_weights = {}
                for move in pacman.move_weights:
                    new_weights[move] = sum(entry[1][move] for entry in elite) / len(elite)
                pacman.move_weights = new_weights

                # Adaptive Mutation: starker Mutationsschub, wenn 5 Generationen ohne Verbesserung
                if no_improvement_counter >= 10:
                    pacman.move_weights = {(0, 1):0.25, (0, -1):0.25, (1, 0):0.25, (-1, 0):0.25}
                  
                elif no_improvement_counter >= 5:
                    pacman.mutate(mutation_rate=0.2, mutation_strength=0.5)
                    no_improvement_counter = 0  # Zähler zurücksetzen
                else:
                    pacman.mutate(mutation_rate=0.05, mutation_strength=0.1)

                generation_data.clear()
            pacman.reset(house_pos)

            # Feste Positionen wiederherstellen
            current_mines = set(initial_mines)
            current_flowers = set(initial_flowers)

        screen.fill(WHITE)
        # In der Hauptschleife, vor draw_full_grid_with_lines():
        update_cell_visits(grid, speed_factor=slider.value)
        draw_full_grid_with_lines(screen, grid)
        overpaint_walls(screen, grid, walls)
        draw_house_marker(screen, grid, house_pos)
        draw_mines(screen, grid, current_mines)
        draw_flowers(screen, grid, current_flowers)
        pacman.draw(screen, grid)
        draw_overlay(screen, pacman, font, width, record_generation, record_survival, slider)
        draw_hovered_cell(screen, grid, pygame.mouse.get_pos(), font)

        pygame.display.flip()
        clock.tick(FPS * slider.value)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
