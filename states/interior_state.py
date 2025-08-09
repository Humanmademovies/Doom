# states/interior_state.py

import pygame
from states.base_state import BaseState
from engine.game_engine import GameEngine

class InteriorState(BaseState):
    """
    Cet état encapsule le moteur de jeu 3D principal.
    Il est responsable de l'initialisation, de la mise à jour et
    du rendu de la partie "Doom-like" du jeu.
    """
    def __init__(self, manager, screen):
        super().__init__(manager)
        
        # --- CORRECTION ---
        # On sauvegarde la référence à l'écran pour pouvoir l'utiliser plus tard.
        self.screen = screen
        
        # On capture et cache la souris pour le mode FPS
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.game_engine = GameEngine(self.screen)

    def update(self, delta_time):
        """
        Délègue la mise à jour et gère les signaux retournés par le moteur de jeu.
        """
        # On s'assure que la souris est bien cachée quand on joue
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        action = self.game_engine.update(delta_time)
        
        # GESTION DES SIGNAUX
        if action == "REQUEST_PAUSE":
            from states.pause_state import PauseState
            # On peut maintenant utiliser self.screen sans erreur
            self.manager.push_state(PauseState(self.manager, self.screen))
            return

        if not self.game_engine.running:
            self.manager.pop_state()

    def render(self, screen):
        """
        Délègue le rendu graphique au moteur de jeu.
        """
        self.game_engine.render()
