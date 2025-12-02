# states/overworld_state.py

import pygame
import sys
from OpenGL.GL import *
from math import sqrt
from config import SCREEN_WIDTH, SCREEN_HEIGHT, OVERWORLD_PLAYER_SPEED
from states.base_state import BaseState
from states.menu_state import MenuState
from states.interior_state import InteriorState
from engine.renderer_2d import Renderer2D
from engine.input_manager import InputManager
from world.map import GameMap
from objects.player import Player

class OverworldState(BaseState):
    """
    Gère le mode de jeu en vue de dessus (Overworld).
    """
    def __init__(self, manager, screen, map_path):
        super().__init__(manager)
        self.screen = screen
        self.input_manager = InputManager()
        self.game_map = GameMap()
        self.renderer_2d = Renderer2D(self.screen)
        
        self.game_map.load_from_file(map_path)
        
        # Le joueur commence au milieu de la 5ème ligne
        start_x = len(self.game_map.grid[0]) / 2
        start_y = 5.0
        self.player = Player(position=[start_x, start_y, 0.0])
        self.player.mode = "2D"
        self.player.size_2d = self.renderer_2d.tile_size * 0.5 # Taille dynamique

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def update(self, delta_time):
        """
        MODIFIÉ: La vérification des transitions est maintenant effectuée AVANT
        la mise à jour du mouvement du joueur pour donner la priorité aux portes.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_state(MenuState(self.manager, self.screen))

        # --- 1. VÉRIFICATION PRIORITAIRE DES TRANSITIONS ---
        # Si le joueur active une porte, la transition se fait immédiatement.
        self._check_for_transitions()
        
        # Si l'état a changé (transition réussie), on arrête la mise à jour ici
        # pour éviter d'exécuter la logique de mouvement inutilement.
        if self.manager.get_active_state() is not self:
            return

        # --- 2. MISE À JOUR DU MOUVEMENT (si aucune transition) ---
        self.input_manager.update()
        movement_vector = self.input_manager.get_movement_vector()
        
        self.player.update(movement_vector, (0,0), delta_time, self.game_map, self.renderer_2d.tile_size)

        # --- 3. MISE À JOUR DE LA CAMÉRA ---
        map_size = (len(self.game_map.grid[0]), len(self.game_map.grid))
        self.renderer_2d.update_camera((self.player.position[0], self.player.position[1]), map_size)

    def _check_for_transitions(self):
        """
        CORRIGÉ: La position de chaque porte est maintenant calculée directement et
        correctement pour une détection de transition fiable.
        """
        player_pos_in_pixels_x = self.player.position[0] * self.renderer_2d.tile_size
        player_pos_in_pixels_y = self.player.position[1] * self.renderer_2d.tile_size
        
        # Le ratio de scaling est constant pour tous les calculs de cette frame
        scale_ratio = (self.renderer_2d.tile_size * 0.5) / 64 # 64 = LOGO_SIZE

        # On parcourt chaque bâtiment pour trouver sa position de base
        for building in self.game_map.building_positions:
            # On calcule la position du coin supérieur gauche du sprite du bâtiment (en pixels)
            building_anchor_x_pixels = building['x'] * self.renderer_2d.tile_size
            building_anchor_y_pixels = building['y'] * self.renderer_2d.tile_size
            
            scaled_building_anchor_x = building['anchor_x'] * scale_ratio
            scaled_building_anchor_y = building['anchor_y'] * scale_ratio
            
            building_top_left_x = building_anchor_x_pixels - scaled_building_anchor_x
            building_top_left_y = building_anchor_y_pixels - scaled_building_anchor_y

            # Maintenant, on vérifie toutes les portes (transitions) associées
            for transition in self.game_map.transition_points:
                # On s'assure que cette transition appartient bien à ce bâtiment
                # (en se basant sur la carte cible, ce qui est une heuristique acceptable ici)
                if transition['target_map'] == building.get('target_map'):
                    
                    # On calcule la position absolue de la porte
                    door_anchor_in_sprite_x, door_anchor_in_sprite_y = transition['anchor_in_sprite']
                    
                    door_center_x_pixels = building_top_left_x + (door_anchor_in_sprite_x * scale_ratio)
                    door_center_y_pixels = building_top_left_y + (door_anchor_in_sprite_y * scale_ratio)

                    # On vérifie la distance entre le joueur et le centre de CETTE porte
                    distance = sqrt((player_pos_in_pixels_x - door_center_x_pixels)**2 + (player_pos_in_pixels_y - door_center_y_pixels)**2)

                    # Le seuil de collision est la moitié de la taille affichée de la porte
                    collision_threshold = (self.renderer_2d.tile_size * 0.5) / 2
                    
                    if distance < collision_threshold:
                        target_map = transition["target_map"]
                        spawn_id = transition["target_spawn_id"]
                        print(f"Transition vers '{target_map}' au point de spawn '{spawn_id}'")
                        
                        self.manager.switch_state(InteriorState(self.manager, self.screen, target_map, spawn_id))
                        return # On quitte dès qu'une transition est trouvée

    def render(self, screen):
        """
        MODIFIÉ: Rendu du mode Overworld utilisant les nouvelles fonctions dynamiques.
        """
        glClearColor(0.0, 0.4, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.renderer_2d.draw_map(self.game_map)
        
        # Dessiner les bâtiments
        for building in self.game_map.building_positions:
            self.renderer_2d.draw_building(building)
        
        # Dessiner le joueur
        player_size_pixels = self.renderer_2d.tile_size * 0.5
        player_pos_pixels_x = self.player.position[0] * self.renderer_2d.tile_size
        player_pos_pixels_y = self.player.position[1] * self.renderer_2d.tile_size
        
        self.renderer_2d.draw_sprite(
            position=(player_pos_pixels_x, player_pos_pixels_y),
            size=(player_size_pixels, player_size_pixels),
            texture_name="pnj/jeanmichel/jeanmichel_idle.png" 
        )

        pygame.display.flip()
