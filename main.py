# main.py

import pygame
import sys
import traceback
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS
from game_state_manager import GameStateManager
from states.menu_state import MenuState # On importe le nouvel état du menu

def main():
    try:
        # Initialisation de Pygame
        pygame.init()
        pygame.display.set_caption("Doom-Like Project")
        # La fenêtre est initialisée avec le support OpenGL, car l'état de jeu en a besoin.
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
        clock = pygame.time.Clock()

        # Création du gestionnaire d'états
        manager = GameStateManager()
        
        # L'état initial est maintenant le MenuState.
        initial_state = MenuState(manager, screen)
        manager.push_state(initial_state)

        # Boucle de jeu principale, gérée par le manager.
        # Elle tournera tant qu'il y aura au moins un état dans la pile.
        while manager.get_active_state() is not None:
            delta_time = clock.tick(TARGET_FPS) / 1000.0
            
            # On délègue les mises à jour et le rendu à l'état actif.
            manager.update(delta_time)
            manager.render(screen)
            
    except Exception as e:
        print(f"Une erreur est survenue : {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
