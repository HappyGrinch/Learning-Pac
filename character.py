import pygame
import random
import time
import math

class PacManAgent:
    def __init__(self, start_pos, cell_size, generation=1):
        """
        start_pos: Tuple (row, col) – Startposition im Grid.
        cell_size: Pixelgröße einer Zelle (wird für die Darstellung benötigt).
        generation: Die Generation des Pac-Man (startet bei 1).
        """
        self.pos = start_pos
        self.cell_size = cell_size
        self.generation = generation
        
        self.movement_history = []
        self.start_time = time.time()
        self.last_food_time = self.start_time
        self.alive = True
        self.survival_time = 0.0
        self.prev_pos = start_pos  # Speichert das Feld vor der letzten Bewegung

        
        # Initiale Gewichtung für Bewegungen: Gleichmäßig auf 0.25 für jede Richtung
        self.move_weights = {
            (0, 1): 0.25,   # Rechts
            (0, -1): 0.25,  # Links
            (1, 0): 0.25,   # Unten
            (-1, 0): 0.25   # Oben
        }
        # Zur Verlangsamung der Bewegung
        self.last_move_time = self.start_time
        self.move_delay = 0.4  # alle 0,4 Sekunden Bewegung

    def get_intelligence(self):
        """
        Berechnet eine Intelligenz-Skala basierend auf dem Unterschied zwischen
        dem höchsten move_weight und dem Basiswert 0.25.
        Initial ergibt das (0.25-0.25)*100 = 0.
        """
        max_weight = max(self.move_weights.values())
        intelligence = round((max_weight - 0.25) * 100)
        return intelligence
    
    def mutate(self, mutation_rate=0.05, mutation_strength=0.1):
        """
        Führt eine Mutation der Bewegungsgewichte durch.
        - mutation_rate: Wahrscheinlichkeit, dass ein Gewicht mutiert.
        - mutation_strength: Maximale prozentuale Veränderung (z. B. ±10%).
        """
        import random
        for move in self.move_weights:
            if random.random() < mutation_rate:
                # Ändere das Gewicht zufällig um bis zu ±mutation_strength
                factor = 1 + random.uniform(-mutation_strength, mutation_strength)
                self.move_weights[move] *= factor
        # Normalisiere die Gewichte, sodass ihre Summe 1 ergibt
        total = sum(self.move_weights.values())
        for move in self.move_weights:
            self.move_weights[move] /= total


    def update(self, grid, obstacles, food_positions, speed_factor=1):
        current_time = time.time()
        self.survival_time = current_time - self.start_time

        # Lebensdauer in echten Sekunden: 20 Sekunden (unabhängig vom speed_factor)
        if current_time - self.last_food_time >= 20:
            self.alive = False

        # Bewegung wird beschleunigt: move_delay wird durch speed_factor geteilt
        if current_time - self.last_move_time >= self.move_delay / speed_factor:
            self.last_move_time = current_time
            move = self.decide_move()
            self.movement_history.append(move)
            self.move(move)

        # Nahrung prüfen (kein Anpassungsfaktor hier, da es real gemessen wird)
        if self.pos in food_positions:
            self.last_food_time = current_time

        # Kollisionen mit Hindernissen:
        if self.pos in obstacles:
            self.alive = False


    def decide_move(self):
            # Berechne alle möglichen Bewegungen
            possible_moves = list(self.move_weights.keys())
            # Filtere, dass die Bewegung nicht zum Feld führt, von dem wir gerade gekommen sind,
            # falls andere Optionen vorhanden sind.
            if self.prev_pos is not None:
                filtered_moves = []
                for move in possible_moves:
                    new_row = self.pos[0] + move[0]
                    new_col = self.pos[1] + move[1]
                    if (new_row, new_col) != self.prev_pos:
                        filtered_moves.append(move)
                if filtered_moves:
                    # Wähle aus den gefilterten Bewegungen, gewichtet nach move_weights
                    weights = [self.move_weights[m] for m in filtered_moves]
                    return random.choices(filtered_moves, weights=weights, k=1)[0]
            # Falls kein Filter möglich, wähle normal:
            weights = list(self.move_weights.values())
            return random.choices(possible_moves, weights=weights, k=1)[0]


    def move(self, move):
        row, col = self.pos
        d_row, d_col = move
        new_row = row + d_row
        new_col = col + d_col
        from settings import GRID_ROWS, GRID_COLS
        if not (0 <= new_row < GRID_ROWS and 0 <= new_col < GRID_COLS):
            self.alive = False
        else:
            self.prev_pos = self.pos  # Speichere aktuelles Feld als vorheriges
            self.pos = (new_row, new_col)

    def draw(self, screen, grid):
        """
        Zeichnet den Pac-Man als blauen Kreis, 
        bei dem ein weißer Keil als Mund ausgespart ist.
        Außerdem wird ein kleines weißes Auge gezeichnet.
        """
        cell_rect = grid[self.pos]["rect"]
        center = cell_rect.center
        radius = cell_rect.width // 2

        # Körper (blauer Kreis)
        pygame.draw.circle(screen, (0, 0, 255), center, radius)

        # Mund (weißer Keil von -30° bis +30°)
        start_angle = -math.pi / 6
        end_angle = math.pi / 6
        step = (end_angle - start_angle) / 12
        mouth_points = [center]
        angle = start_angle
        while angle <= end_angle:
            x = center[0] + int(radius * math.cos(angle))
            y = center[1] + int(radius * math.sin(angle))
            mouth_points.append((x, y))
            angle += step
        pygame.draw.polygon(screen, (255, 255, 255), mouth_points)

        # Auge (weißer Punkt) etwas nach oben
        eye_offset_x = int(radius * 0.2)
        eye_offset_y = int(-0.6 * radius)
        eye_center = (center[0] + eye_offset_x, center[1] + eye_offset_y)
        eye_radius = max(1, radius // 8)
        pygame.draw.circle(screen, (255, 255, 255), eye_center, eye_radius)

    def reinforce(self, reward):
        """
        Einfaches Lernschema: Erhöhe die Gewichtung aller Moves 
        proportional zum reward und normalisiere.
        """
        if not self.movement_history:
            return
        for move in self.movement_history:
            self.move_weights[move] += reward / len(self.movement_history)
        total = sum(self.move_weights.values())
        for move in self.move_weights:
            self.move_weights[move] /= total

    def reset(self, new_start):
        """
        Setzt den Pac-Man an eine neue Startposition, 
        behält seine gelernten move_weights und erhöht NICHT automatisch die Generation.
        (Das erfolgt in main.py, wenn Pac-Man stirbt.)
        """
        self.pos = new_start
        self.start_time = time.time()
        self.last_food_time = self.start_time
        self.alive = True
        self.survival_time = 0.0
        self.movement_history = []
        self.last_move_time = self.start_time
