import random
import pygame
import time

def generate_mines(grid, walls, house_pos, num_mines):
    """
    Generiert num_mines zufällig platzierte Minen auf dem Grid.
    Nur freie Zellen, die weder zu den Bunkerwänden noch dem Haus gehören.
    """
    available_positions = [pos for pos in grid.keys() if pos not in walls and pos != house_pos]
    if num_mines > len(available_positions):
        num_mines = len(available_positions)
    return set(random.sample(available_positions, num_mines))

def draw_mines(screen, grid, mines):
    """
    Zeichnet die Minen als schwarze Quadrate.
    """
    for pos in mines:
        rect = grid[pos]["rect"]
        pygame.draw.rect(screen, (0, 0, 0), rect)

def explosion_animation(screen, grid, pos):
    """
    Führt eine Explosion-Animation an der Zelle pos aus.
    Ein roter Kreis expandiert innerhalb von 0,5 Sekunden.
    """
    rect = grid[pos]["rect"]
    center = rect.center
    max_radius = rect.width
    duration = 0.5
    start_time = time.time()
    while time.time() - start_time < duration:
        t = time.time() - start_time
        progress = t / duration
        current_radius = int(max_radius * progress)
        pygame.draw.rect(screen, (255, 255, 255), rect)
        pygame.draw.circle(screen, (255, 0, 0), center, current_radius)
        pygame.display.flip()
    pygame.draw.rect(screen, (255, 255, 255), rect)

def play_explosion_sound():
    try:
        explosion_sound = pygame.mixer.Sound("explosion.wav")
        explosion_sound.play()
    except Exception as e:
        print("Explosion sound konnte nicht geladen werden:", e)
