import pygame
import random
import time
import math

class PacManAgent:
    def __init__(self, start_pos, cell_size, generation=1):
        """
        start_pos: Tuple (row, col) – Startposition im Grid.
        cell_size: Pixelgröße einer Zelle.
        generation: Startgeneration (standardmäßig 1).
        """
        self.pos = start_pos
        self.cell_size = cell_size
        self.generation = generation

        self.start_time = time.time()
        self.last_food_time = self.start_time
        self.alive = True
        self.survival_time = 0.0

        # Q-Tabelle: Zustand (Position) -> { Aktion: Q-Wert }
        # Wir verwenden als Zustand einfach die Position (row, col).
        self.Q = {}
        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        self._initialize_state(self.pos)

        # Parameter für Q-Learning
        self.epsilon = 0.1    # Explorationsrate (epsilon-greedy)
        self.alpha = 0.5      # Lernrate
        self.gamma = 0.9      # Diskontfaktor

        self.last_move_time = self.start_time
        self.move_delay = 0.4  # Zeit zwischen Bewegungen (in Sekunden)

        self.prev_state = None
        self.prev_action = None

        self.prev_pos = start_pos  # Verhindert direkten Rückweg

    def _initialize_state(self, state):
        if state not in self.Q:
            self.Q[state] = {action: 0.0 for action in self.actions}

    def get_action(self, state):
        self._initialize_state(state)
        # Epsilon-greedy Auswahl:
        if random.random() < self.epsilon:
            possible_actions = list(self.Q[state].keys())
            # Vermeide den unmittelbaren Rückweg, falls möglich:
            if self.prev_pos is not None:
                filtered = [a for a in possible_actions if (state[0] + a[0], state[1] + a[1]) != self.prev_pos]
                if filtered:
                    possible_actions = filtered
            return random.choice(possible_actions)
        else:
            max_q = max(self.Q[state].values())
            best_actions = [a for a, q in self.Q[state].items() if q == max_q]
            if self.prev_pos is not None:
                filtered = [a for a in best_actions if (state[0] + a[0], state[1] + a[1]) != self.prev_pos]
                if filtered:
                    best_actions = filtered
            return random.choice(best_actions)

    def update(self, grid, obstacles, food_positions, speed_factor=1):
        current_time = time.time()
        self.survival_time = current_time - self.start_time

        # Tod, wenn 20 echte Sekunden ohne Nahrung vergangen sind:
        if current_time - self.last_food_time >= 20:
            self.alive = False

        # Bewegung erfolgt beschleunigt über den speed_factor:
        if current_time - self.last_move_time >= self.move_delay / speed_factor:
            self.last_move_time = current_time
            state = self.pos
            action = self.get_action(state)
            self.prev_state = state
            self.prev_action = action
            self.prev_pos = self.pos
            self.move(action)

        # Nahrung prüfen:
        if self.pos in food_positions:
            self.last_food_time = current_time

        # Kollision mit Hindernissen:
        if self.pos in obstacles:
            self.alive = False

    def move(self, action):
        row, col = self.pos
        d_row, d_col = action
        new_state = (row + d_row, col + d_col)
        from settings import GRID_ROWS, GRID_COLS
        if not (0 <= new_state[0] < GRID_ROWS and 0 <= new_state[1] < GRID_COLS):
            self.alive = False
        else:
            self._initialize_state(new_state)
            self.pos = new_state

    def learn(self, reward, new_state):
        self._initialize_state(new_state)
        old_q = self.Q[self.prev_state][self.prev_action]
        max_next = max(self.Q[new_state].values())
        self.Q[self.prev_state][self.prev_action] = old_q + self.alpha * (reward + self.gamma * max_next - old_q)

    def compute_intelligence(self, record_survival):
        """
        Berechnet einen Intelligenzwert, der ausdrückt, wie gut der Agent im Vergleich zu seinen
        vorherigen Generationen ist. Dazu werden zwei Faktoren kombiniert:
          - Überlebensfaktor: (eigene Überlebenszeit / record_survival)
          - Lernfaktor: max(Q[state]) im aktuellen Zustand (sofern > 0; sonst 0)
        Falls record_survival 0 ist, wird der Überlebensfaktor als 1 angenommen.
        Beide Faktoren werden gleich gewichtet und mit 100 skaliert.
        """
        if record_survival > 0:
            survival_factor = self.survival_time / record_survival
        else:
            survival_factor = 1
        self._initialize_state(self.pos)
        learning_factor = max(0, max(self.Q[self.pos].values()))
        # Kombiniere beide Faktoren (0.5 * survival + 0.5 * learning), skaliere mit 100:
        intelligence = (0.5 * survival_factor + 0.5 * learning_factor) * 100
        return intelligence

    def get_intelligence(self):
        """
        Standardvariante ohne Vergleich zu einer vorherigen Generation.
        Hier geben wir einfach den maximalen Q-Wert im aktuellen Zustand (multipliziert mit 100) zurück.
        Für eine sinnvolle Bewertung im Kontext des Lernens über Generationen sollte compute_intelligence(record_survival)
        verwendet werden.
        """
        self._initialize_state(self.pos)
        max_q = max(self.Q[self.pos].values())
        return round(max_q * 100)

    def draw(self, screen, grid):
        cell_rect = grid[self.pos]["rect"]
        center = cell_rect.center
        radius = cell_rect.width // 2
        # Zeichne den Körper als blauen Kreis
        pygame.draw.circle(screen, (0, 0, 255), center, radius)
        # Zeichne den Mund als weißen Keil (Bogen von -30° bis +30°)
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
        # Zeichne das Auge als kleinen weißen Kreis, etwas höher platziert
        eye_offset_x = int(radius * 0.2)
        eye_offset_y = int(-0.6 * radius)
        eye_center = (center[0] + eye_offset_x, center[1] + eye_offset_y)
        eye_radius = max(1, radius // 8)
        pygame.draw.circle(screen, (255, 255, 255), eye_center, eye_radius)

    def reinforce(self, reward):
        if self.prev_state is not None and self.prev_action is not None:
            self.learn(reward, self.pos)

    def mutate(self, mutation_rate=0.05, mutation_strength=0.1):
        for state in self.Q:
            for action in self.Q[state]:
                if random.random() < mutation_rate:
                    factor = 1 + random.uniform(-mutation_strength, mutation_strength)
                    self.Q[state][action] *= factor
            total = sum(self.Q[state].values())
            if total != 0:
                for action in self.Q[state]:
                    self.Q[state][action] /= total

    def reset(self, new_start):
        self.pos = new_start
        self.start_time = time.time()
        self.last_food_time = self.start_time
        self.alive = True
        self.survival_time = 0.0
        self.prev_state = None
        self.prev_action = None
        self.last_move_time = self.start_time
