# states/interior_state.py

import pygame
from states.base_state import BaseState
from engine.game_engine import GameEngine
# NOUVEL IMPORT
from states.game_over_state import GameOverState


class InteriorState(BaseState):
    """
    Cet état encapsule le moteur de jeu 3D principal.
    Il est responsable de l'initialisation, de la mise à jour et
    du rendu de la partie "Doom-like" du jeu.
    """
    def __init__(self, manager, screen, map_path, spawn_id=None): # Ajout de spawn_id
        super().__init__(manager)
        
        self.screen = screen
        
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # On passe le chemin de la carte ET le spawn_id au moteur de jeu
        self.game_engine = GameEngine(self.screen, map_path, spawn_id)

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

        # CORRECTION : On PUSH le nouvel état au lieu de faire un SWITCH.
        # Cela permet à l'InteriorState de rester en arrière-plan.
        if action == "GAME_OVER":
            self.manager.push_state(GameOverState(self.manager, self.screen))
            return

        if not self.game_engine.running:
            self.manager.pop_state()

    def render(self, screen):
        """
        Délègue le rendu graphique au moteur de jeu.
        """
        self.game_engine.render()
