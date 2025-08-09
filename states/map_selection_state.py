# states/map_selection_state.py

import pygame
import sys
import os
from OpenGL.GL import *

from states.base_state import BaseState
from states.interior_state import InteriorState
from ui.button import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class MapSelectionState(BaseState):
    """
    Gère l'écran de sélection de la carte.
    """
    def __init__(self, manager, screen):
        super().__init__(manager)
        self.screen = screen
        
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        try:
            self.font = pygame.font.Font("assets/ui/PressStart2P-Regular.ttf", 20)
        except pygame.error:
            self.font = pygame.font.Font(None, 32)

        self.buttons = []
        self._create_map_buttons()

    def _create_map_buttons(self):
        """Scanne le dossier des cartes et crée un bouton pour chaque fichier .json."""
        maps_path = "assets/maps/"
        try:
            map_files = [f for f in os.listdir(maps_path) if f.endswith('.json')]
        except FileNotFoundError:
            map_files = []
            print(f"Erreur: Le dossier des cartes '{maps_path}' est introuvable.")

        center_x = self.screen.get_width() / 2
        start_y = 150
        
        for i, map_file in enumerate(map_files):
            map_name = os.path.splitext(map_file)[0].replace('_', ' ').title()
            map_path = os.path.join(maps_path, map_file)
            
            button = Button(
                x=center_x - 200, y=start_y + i * 70, width=400, height=50,
                text=map_name,
                # La fonction lambda est une astuce pour passer le chemin de la carte au callback
                callback=lambda path=map_path: self.start_game_with_map(path)
            )
            self.buttons.append(button)

    def start_game_with_map(self, map_path):
        """Lance l'état de jeu avec la carte sélectionnée."""
        # On doit modifier InteriorState et GameEngine pour qu'ils acceptent un chemin de carte
        next_state = InteriorState(self.manager, self.screen, map_path)
        self.manager.switch_state(next_state)

    def update(self, delta_time):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in self.buttons:
                button.handle_event(event)

        for button in self.buttons:
            button.update(mouse_pos)

    def render(self, screen):
        """Affiche la liste des cartes."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        for button in self.buttons:
            # On réutilise la même fonction de dessin que les autres menus
            button.draw(self._draw_text)
        
        pygame.display.flip()

    def _draw_text(self, text, x, y, dry_run=False):
        """Méthode de rendu de texte (similaire à MenuState)."""
        surface = self.font.render(text, True, (255, 255, 255))
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
        glDeleteTextures(texture_id)
