# states/map_selection_state.py

import sys
import os
import pygame
from OpenGL.GL import *
from states.base_state import BaseState
from states.interior_state import InteriorState
from states.overworld_state import OverworldState
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class MapSelectionState(BaseState):
    def __init__(self, manager, screen):
        super().__init__(manager)
        self.screen = screen
        self.maps_folder = "assets/maps"
        self.map_files = self._get_map_files()
        self.selected_map_index = 0
        try:
            self.font = pygame.font.Font("assets/ui/PressStart2P-Regular.ttf", 20)
        except pygame.error:
            self.font = pygame.font.Font(None, 32)
        
    def _get_map_files(self):
        files = [f for f in os.listdir(self.maps_folder) if f.endswith('.json')]
        return files

    def update(self, delta_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_map_index = (self.selected_map_index - 1) % len(self.map_files)
                elif event.key == pygame.K_DOWN:
                    self.selected_map_index = (self.selected_map_index + 1) % len(self.map_files)
                elif event.key == pygame.K_RETURN:
                    self.start_game_with_map()

    def render(self, screen):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        title_text = "Select a Map"
        title_width, title_height = self._draw_text(title_text, 0, 0, dry_run=True)
        self._draw_text(title_text, (SCREEN_WIDTH - title_width) // 2, 50)
        
        for i, map_file in enumerate(self.map_files):
            color = (255, 255, 255) if i != self.selected_map_index else (255, 200, 0)
            map_text = map_file
            text_width, text_height = self._draw_text(map_text, 0, 0, color, dry_run=True)
            self._draw_text(map_text, (SCREEN_WIDTH - text_width) // 2, 150 + i * 50, color)
        
        pygame.display.flip()

    def _draw_text(self, text, x, y, color=(255, 255, 255), dry_run=False):
        surface = self.font.render(text, True, color)
        width, height = surface.get_size()
        if dry_run: return width, height

        texture_data = pygame.image.tostring(surface, "RGBA", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 0); glVertex2f(x, y + height)
        glEnd()
        
        glDeleteTextures(int(texture_id))

    def start_game_with_map(self):
        from gameplay.game_session import GameSession
        self.manager.game_session = GameSession()

        selected_map_file = self.map_files[self.selected_map_index]
        map_path = os.path.join(self.maps_folder, selected_map_file)
        
        # On force la carte choisie dans la session
        self.manager.game_session.current_map = map_path
        
        if selected_map_file.startswith("int_"):
            print(f"Lancement manuel INT : {map_path}")
            self.manager.switch_state(InteriorState(self.manager, self.screen, map_path))
        elif selected_map_file.startswith("ext_"):
            print(f"Lancement manuel EXT : {map_path}")
            self.manager.switch_state(OverworldState(self.manager, self.screen, map_path))
        else:
            print(f"Erreur: Type de carte inconnu pour {selected_map_file}")
