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
    def __init__(self, manager, screen, map_path, spawn_id=None): 
        super().__init__(manager)
        
        self.screen = screen
        
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # CORRECTION : On passe explicitement la session au moteur
        self.game_engine = GameEngine(self.screen, map_path, spawn_id, self.manager.game_session)

        # Injection des stats (PV, Armes...) dans le joueur du moteur
        if self.manager.game_session:
            self.manager.game_session.apply_to_player(self.game_engine.player)
            
        # Raccourci pour que le GameStateManager puisse trouver le joueur lors de la sauvegarde
        self.player = self.game_engine.player

    def update(self, delta_time):
        """
        Délègue la mise à jour et gère les signaux retournés par le moteur de jeu.
        """
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        action = self.game_engine.update(delta_time)
        
        if action == "REQUEST_PAUSE":
            from states.pause_state import PauseState
            self.manager.push_state(PauseState(self.manager, self.screen))
            return

        if action == "GAME_OVER":
            self.manager.push_state(GameOverState(self.manager, self.screen))
            return
            
        # NOUVEAU BLOC : Gestion de la sortie vers l'Overworld
        if isinstance(action, dict) and action.get("type") == "EXIT_TO_MAP":
            target_map = action["target"]
            print(f"Sortie du niveau vers : {target_map}")
            
            # Sauvegarde des stats actuelles (PV, munitions) avant de partir
            if self.manager.game_session:
                self.manager.game_session.save_player_state(self.player)
                self.manager.game_session.current_map = target_map
            
            # Retour à l'Overworld
            from states.overworld_state import OverworldState
            self.manager.switch_state(OverworldState(self.manager, self.screen, target_map))
            return

        if not self.game_engine.running:
            self.manager.pop_state()

    def render(self, screen):
        """
        Délègue le rendu graphique au moteur de jeu.
        """
        self.game_engine.render()
