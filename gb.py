# generate_building.py

import pygame
import os
import sys
import random

def create_logo_surface():
    """Crée une surface de 64x64 pixels pour le logo (porte)."""
    logo_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(logo_surface, (100, 100, 100), (0, 0, 64, 64))
    pygame.draw.rect(logo_surface, (0, 0, 0), (0, 24, 64, 16)) # Horizontale
    pygame.draw.rect(logo_surface, (0, 0, 0), (24, 0, 16, 64)) # Verticale
    return logo_surface

def generate_building_sprite(name, width, height, orientation, num_doors, folder="assets/sprites/"):
    """
    MODIFIÉ: Génère une image de bâtiment avec un nombre variable de portes
    placées aléatoirement sur un seul côté.
    """
    if orientation not in ['N', 'E', 'S', 'O']:
        print("Erreur: L'orientation doit être N, E, S ou O.")
        return
    if num_doors < 0:
        print("Erreur: Le nombre de portes ne peut pas être négatif.")
        return

    LOGO_SIZE = 64
    margin = 64 # Marge pour la porte si elle est au Nord ou à l'Ouest

    # Ajout d'une variation aléatoire à la dimension du côté des portes
    dimension_bonus = random.randint(0, 32)
    
    # Détermination de la dimension principale et de la longueur du côté des portes
    if orientation in ['N', 'S']:
        side_length = width + dimension_bonus
        main_dimension = height
    else: # 'E', 'O'
        side_length = height + dimension_bonus
        main_dimension = width

    # Vérification de la faisabilité
    if num_doors * LOGO_SIZE > side_length:
        print(f"Erreur: Impossible de placer {num_doors} portes de {LOGO_SIZE}px sur un côté de {side_length}px.")
        return

    # Calcul de la taille finale de l'image
    total_width = side_length if orientation in ['N', 'S'] else main_dimension + margin
    total_height = main_dimension + margin if orientation in ['N', 'S'] else side_length
    final_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    
    # Dessin du rectangle du bâtiment
    building_rect = pygame.Rect(0, 0, width, height)
    if orientation == 'O': building_rect.left = margin
    if orientation == 'N': building_rect.top = margin
    pygame.draw.rect(final_surface, (180, 180, 180), building_rect)

    # Placement des portes
    if num_doors > 0:
        logo_surface = create_logo_surface()
        
        # On calcule les positions possibles pour commencer à dessiner un logo
        available_slots = side_length - (num_doors * LOGO_SIZE)
        
        # On génère des points de séparation aléatoires
        split_points = sorted([random.randint(0, available_slots) for _ in range(num_doors - 1)])
        
        # On calcule les espaces entre chaque porte
        gaps = [split_points[0]]
        for i in range(len(split_points) - 1):
            gaps.append(split_points[i+1] - split_points[i])
        gaps.append(available_slots - split_points[-1] if num_doors > 1 else available_slots)
        
        current_pos = 0
        for i in range(num_doors):
            current_pos += gaps[i]
            
            logo_x, logo_y = 0, 0
            if orientation == 'N':
                logo_x = current_pos
                logo_y = 0
            elif orientation == 'S':
                logo_x = current_pos
                logo_y = main_dimension
            elif orientation == 'E':
                logo_x = main_dimension
                logo_y = current_pos
            elif orientation == 'O':
                logo_x = 0
                logo_y = current_pos
            
            final_surface.blit(logo_surface, (logo_x, logo_y))
            current_pos += LOGO_SIZE

    # Sauvegarde de l'image
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, f"{name}.png")
    pygame.image.save(final_surface, filepath)
    print(f"Bâtiment '{name}.png' généré avec succès dans {folder}")


if __name__ == "__main__":
    print("--- Générateur de Bâtiment de Test Amélioré ---")
    try:
        name = input("Nom du bâtiment (ex: 'maison_test'): ")
        width = int(input("Largeur de base en pixels (ex: 128): "))
        height = int(input("Hauteur de base en pixels (ex: 128): "))
        orientation = input("Orientation des portes (N, E, S, O): ").upper()
        num_doors = int(input("Nombre de portes à générer (ex: 2, 0 si aucune): "))
    except ValueError:
        print("Erreur: Les dimensions et le nombre de portes doivent être des nombres entiers.")
        sys.exit(1)
    
    pygame.init()
    generate_building_sprite(name, width, height, orientation, num_doors)
    pygame.quit()
