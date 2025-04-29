# main.py

import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from engine.game_engine import GameEngine
import traceback

def main():
    try:
        # Initialisation de Pygame
        pygame.init()
        pygame.display.set_caption("Doom-Like Project")
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)

        # Création de l'instance du moteur de jeu
        game_engine = GameEngine(screen)

        # Lancement de la boucle principale du jeu
        game_engine.run()

    except Exception as e:
        print(f"Une erreur est survenue : {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
