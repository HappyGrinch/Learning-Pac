import random
import pygame
import time

def generate_mines(grid, walls, house_pos, num_mines):
    """
    Generiert num_mines zufällig platzierte Minen auf dem Grid.
    Es werden nur freie Zellen ausgewählt, die weder zu den Bunkerwänden (walls)
    noch der Hausposition (house_pos) zugeordnet sind.
    """
    available_positions = [pos for pos in grid.keys() if pos not in walls and pos != house_pos]
    if num_mines > len(available_positions):
        num_mines = len(available_positions)
    mines = set(random.sample(available_positions, num_mines))
    return mines

def draw_mines(screen, grid, mines):
    """
    Zeichnet die Minen als schwarze Quadrate.
    """
    for pos in mines:
        rect = grid[pos]["rect"]
        pygame.draw.rect(screen, (0, 0, 0), rect)

def explosion_animation(screen, grid, pos):
    """
    Führt eine einfache Explosion-Animation an der Zelle pos aus.
    Dabei wird ein roter Kreis expandiert, der nach 0,5 Sekunden wieder verschwindet.
    """
    rect = grid[pos]["rect"]
    center = rect.center
    max_radius = rect.width  # maximal so groß wie die Zelle
    duration = 0.5  # Dauer der Animation in Sekunden
    start_time = time.time()
    while time.time() - start_time < duration:
        t = time.time() - start_time
        progress = t / duration  # 0 bis 1
        current_radius = int(max_radius * progress)
        # Fülle das Feld zunächst weiß, um vorherige Zeichnungen zu überdecken
        pygame.draw.rect(screen, (255, 255, 255), rect)
        # Zeichne den expandierenden roten Kreis
        pygame.draw.circle(screen, (255, 0, 0), center, current_radius)
        pygame.display.flip()
    # Nach der Animation das Feld leeren
    pygame.draw.rect(screen, (255, 255, 255), rect)

def play_explosion_sound():
    """
    Spielt den Explosionssound ab.
    Erwartet, dass die Datei 'explosion.wav' im selben Verzeichnis liegt.
    """
    try:
        explosion_sound = pygame.mixer.Sound("explosion.wav")
        explosion_sound.play()
    except Exception as e:
        print("Explosion sound konnte nicht geladen werden:", e)
