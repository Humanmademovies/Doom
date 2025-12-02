import pygame
import os

def create_door_texture():
    pygame.init()
    size = 64
    surface = pygame.Surface((size, size))
    
    # Fond bois/métal
    surface.fill((100, 50, 20)) # Marron foncé
    
    # Cadre
    pygame.draw.rect(surface, (80, 40, 10), (0,0,size,size), 4)
    
    # Planches verticales
    for i in range(1, 4):
        x = i * (size // 4)
        pygame.draw.line(surface, (60, 30, 5), (x, 0), (x, size), 2)
        
    # Poignée
    pygame.draw.circle(surface, (200, 200, 0), (size - 10, size // 2), 4)
    
    if not os.path.exists("assets/textures"):
        os.makedirs("assets/textures")
        
    pygame.image.save(surface, "assets/textures/door.png")
    print("Texture assets/textures/door.png générée.")

if __name__ == "__main__":
    create_door_texture()
