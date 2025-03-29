import random
import pygame
import time

def generate_flowers(grid, walls, house_pos, mines_positions, num_flowers):
    """
    Generiert num_flowers zufällig platzierte Blumen auf dem Grid.
    Nur Zellen, die nicht zu den Wänden, Minen oder dem Haus gehören.
    """
    available_positions = [
        pos for pos in grid.keys()
        if pos not in walls and pos not in mines_positions and pos != house_pos
    ]
    if num_flowers > len(available_positions):
        num_flowers = len(available_positions)
    return set(random.sample(available_positions, num_flowers))

def draw_flowers(screen, grid, flowers):
    """
    Zeichnet die Blumen als grüne Blume:
    Ein grüner Kreis (Blütenblatt) mit einem kleineren gelben Kreis (Blütenmitte).
    """
    for pos in flowers:
        rect = grid[pos]["rect"]
        center = rect.center
        radius = rect.width // 2 - 2
        pygame.draw.circle(screen, (0, 255, 0), center, radius)
        inner_radius = max(1, radius // 2)
        pygame.draw.circle(screen, (255, 255, 0), center, inner_radius)

def eating_animation(screen, grid, pos, pacman):
    """
    Führt eine Essensanimation an der Zelle pos aus.
    Simuliert, dass Pac-Man seinen Mund dreimal auf- und zuklappt.
    """
    rect = grid[pos]["rect"]
    center = rect.center
    radius = rect.width // 2
    for _ in range(3):
        pygame.draw.circle(screen, (0, 0, 255), center, radius)
        pygame.display.flip()
        pygame.time.delay(100)
        pacman.draw(screen, grid)
        pygame.display.flip()
        pygame.time.delay(100)

def play_eating_sound():
    try:
        eating_sound = pygame.mixer.Sound("eating.wav")
        eating_sound.play()
    except Exception as e:
        print("Eating sound konnte nicht geladen werden:", e)
