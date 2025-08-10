# states/overworld_state.py

import pygame
import sys
from OpenGL.GL import *
from config import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPRITE_SIZE, OVERWORLD_PLAYER_SPEED, OVERWORLD_TILES_PER_SCREEN_HEIGHT
from states.base_state import BaseState
from states.menu_state import MenuState
from states.interior_state import InteriorState
from engine.renderer_2d import Renderer2D
from engine.input_manager import InputManager
from world.map import GameMap
from objects.player import Player
from math import sqrt

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
        
        self.player = Player(position=[5.0, 5.0, 0.0])
        self.player.mode = "2D"

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def update(self, delta_time):
        """
        Logique de mise à jour du mode Overworld.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_state(MenuState(self.manager, self.screen))

        self.input_manager.update()
        movement_vector = self.input_manager.get_movement_vector()
        
        self.player.update(movement_vector, (0,0), delta_time, self.game_map, self.renderer_2d.tile_size)

        map_size = (len(self.game_map.grid[0]), len(self.game_map.grid))
        self.renderer_2d.update_camera((self.player.position[0], self.player.position[1]), map_size)

        self._check_for_transitions()

    def _check_for_transitions(self):
        """Vérifie si le joueur est sur une porte et déclenche la transition."""
        player_x = self.player.position[0]
        player_y = self.player.position[1]
        
        for transition in self.game_map.transition_points:
            trans_x, trans_y = transition["position"]
            
            distance = sqrt((player_x - trans_x)**2 + (player_y - trans_y)**2)
            
            if distance < 0.5:
                print(f"Collision avec un point de transition ! Changement d'état.")
                target_map = transition["target_map"]
                self.manager.switch_state(InteriorState(self.manager, self.screen, target_map))
                return

    def render(self, screen):
        """
        Rendu du mode Overworld.
        """
        glClearColor(0.0, 0.4, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.renderer_2d.draw_map(self.game_map)
        
        sprites_to_draw = []

        sprites_to_draw.append({
            "position": (self.player.position[0] * self.renderer_2d.tile_size, self.player.position[1] * self.renderer_2d.tile_size),
            "texture": "pnj/jeanmichel/jeanmichel_idle.png",
            "size": PLAYER_SPRITE_SIZE
        })
        
        for building in self.game_map.building_positions:
            sprites_to_draw.append({
                "position": (building["x"] * self.renderer_2d.tile_size, building["y"] * self.renderer_2d.tile_size),
                "texture": f"sprites/{building['sprite']}",
                "size": building.get('size', self.renderer_2d.tile_size)
            })
        
        self.renderer_2d.draw_sprites(sprites_to_draw)

        pygame.display.flip()
