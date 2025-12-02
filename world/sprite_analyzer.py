# world/sprite_analyzer.py

import pygame

def create_logo_definition(size=64, bar_thickness=16):
    """
    Crée la définition du logo (croix noire sur fond gris foncé)
    pour une taille donnée.
    """
    logo_def = []
    half_size = size // 2
    half_bar = bar_thickness // 2
    
    for y in range(size):
        row = []
        for x in range(size):
            # Vérifie si le pixel est dans la barre horizontale ou verticale
            if (half_size - half_bar <= x < half_size + half_bar) or \
               (half_size - half_bar <= y < half_size + half_bar):
                row.append((0, 0, 0)) # Noir
            else:
                row.append((100, 100, 100)) # Gris foncé
        logo_def.append(row)
        
    return logo_def

LOGO_DEFINITION = create_logo_definition()
LOGO_SIZE = 64

def find_logo_positions(sprite_path):
    """
    Scanne un sprite à la recherche de notre "logo de porte"
    et retourne les coordonnées de ses coins supérieurs gauches.
    """
    try:
        image = pygame.image.load(sprite_path).convert()
    except pygame.error as e:
        print(f"Erreur de chargement d'image pour l'analyse de sprite: {e}")
        return []

    image_width, image_height = image.get_size()
    logo_positions = []

    for y in range(image_height - LOGO_SIZE + 1):
        for x in range(image_width - LOGO_SIZE + 1):
            is_match = True
            
            for ly in range(LOGO_SIZE):
                for lx in range(LOGO_SIZE):
                    if x + lx >= image_width or y + ly >= image_height:
                        is_match = False
                        break
                    
                    pixel_color = image.get_at((x + lx, y + ly))
                    
                    if (pixel_color.r, pixel_color.g, pixel_color.b) != LOGO_DEFINITION[ly][lx]:
                        is_match = False
                        break
                if not is_match:
                    break
            
            if is_match:
                logo_positions.append((x, y))

    return logo_positions
