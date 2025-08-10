# generate_building.py

import pygame
import os
import sys

def create_logo_surface():
    """
    Crée une surface de 64x64 pixels pour le logo, avec un fond gris foncé et
    une croix noire de 16px d'épaisseur.
    """
    logo_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # Dessine un carré gris foncé
    pygame.draw.rect(logo_surface, (100, 100, 100), (0, 0, 64, 64))
    
    # Dessine la croix noire de 16 pixels d'épaisseur
    # Barre horizontale
    pygame.draw.rect(logo_surface, (0, 0, 0), (0, 24, 64, 16))
    # Barre verticale
    pygame.draw.rect(logo_surface, (0, 0, 0), (24, 0, 16, 64))
    
    return logo_surface


def generate_building_sprite(name, width, height, orientation, folder="assets/sprites/"):
    """
    Génère une image de bâtiment avec une marge transparente et un logo de porte.
    """
    if orientation not in ['N', 'E', 'S', 'O']:
        print("Erreur: L'orientation doit être N, E, S ou O.")
        return

    margin = 64
    logo_size = 64

    total_width = width + margin if orientation in ['O', 'E'] else width
    total_height = height + margin if orientation in ['N', 'S'] else height

    final_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    
    building_rect = pygame.Rect(0, 0, width, height)
    if orientation == 'O':
        building_rect.left = margin
    if orientation == 'N':
        building_rect.top = margin

    pygame.draw.rect(final_surface, (180, 180, 180), building_rect)

    logo_surface = create_logo_surface()
    
    logo_pos_x, logo_pos_y = 0, 0
    if orientation == 'N':
        logo_pos_x = (total_width - logo_size) // 2
        logo_pos_y = 0
    elif orientation == 'S':
        logo_pos_x = (total_width - logo_size) // 2
        logo_pos_y = height
    elif orientation == 'E':
        logo_pos_x = width
        logo_pos_y = (total_height - logo_size) // 2
    elif orientation == 'O':
        logo_pos_x = 0
        logo_pos_y = (total_height - logo_size) // 2
    
    final_surface.blit(logo_surface, (logo_pos_x, logo_pos_y))
            
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{name}.png"
    filepath = os.path.join(folder, filename)
    pygame.image.save(final_surface, filepath)
    
    print(f"Bâtiment '{filename}' de {width}x{height} généré avec une porte au {orientation} et sauvegardé dans {folder}")


if __name__ == "__main__":
    
    print("--- Générateur de Bâtiment de Test ---")
    try:
        name = input("Nom du bâtiment (ex: 'maison_test'): ")
        width = int(input("Largeur du bâtiment en pixels (ex: 64): "))
        height = int(input("Hauteur du bâtiment en pixels (ex: 64): "))
        orientation = input("Orientation de la porte (N, E, S, O): ").upper()
    except ValueError:
        print("Erreur: Les dimensions doivent être des nombres entiers.")
        sys.exit(1)
    
    pygame.init()
    generate_building_sprite(name, width, height, orientation)
