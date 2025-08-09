# states/game_over_state.py

import pygame
import sys
from OpenGL.GL import *

from states.base_state import BaseState
from ui.button import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT

# Imports pour le "type hinting" afin d'éviter les imports circulaires
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_state_manager import GameStateManager
    from states.menu_state import MenuState
    from states.interior_state import InteriorState

class GameOverState(BaseState):
    """
    Gère l'écran de Game Over.
    """
    def __init__(self, manager: 'GameStateManager', screen):
        super().__init__(manager)
        self.screen = screen

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        try:
            self.title_font = pygame.font.Font("assets/ui/PressStart2P-Regular.ttf", 48)
            self.font = pygame.font.Font("assets/ui/PressStart2P-Regular.ttf", 24)
        except pygame.error:
            self.title_font = pygame.font.Font(None, 70)
            self.font = pygame.font.Font(None, 40)

        # Création des boutons
        self.buttons = []
        center_x = self.screen.get_width() / 2
        
        btn_recommencer = Button(
            x=center_x - 150, y=350, width=300, height=50,
            text="Recommencer", callback=self.restart_level
        )
        btn_menu_principal = Button(
            x=center_x - 150, y=430, width=300, height=50,
            text="Menu Principal", callback=self.back_to_main_menu
        )
        self.buttons.extend([btn_recommencer, btn_menu_principal])

    def restart_level(self):
        """Recharge le niveau actuel en créant un nouvel InteriorState."""
        from states.interior_state import InteriorState
        
        game_state = None
        for state in reversed(self.manager.states):
            if isinstance(state, InteriorState):
                game_state = state
                break
        
        if game_state:
            map_path = game_state.game_engine.map_path
            self.manager.switch_state(InteriorState(self.manager, self.screen, map_path))
        else:
            self.back_to_main_menu()


    def back_to_main_menu(self):
        """Retourne au menu principal."""
        from states.menu_state import MenuState
        self.manager.switch_state(MenuState(self.manager, self.screen))

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
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(0.6, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(SCREEN_WIDTH, 0)
        glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
        glVertex2f(0, SCREEN_HEIGHT)
        glEnd()
        
        title_w, title_h = self._draw_text("GAME OVER", 0, 0, self.title_font, dry_run=True)
        self._draw_text("GAME OVER", SCREEN_WIDTH / 2 - title_w / 2, 200, self.title_font)
        
        for button in self.buttons:
            button.draw(self._draw_text_button)
        
        glEnable(GL_DEPTH_TEST)
        pygame.display.flip()
        
    def _draw_text_button(self, text, x, y, dry_run=False):
        """Wrapper pour utiliser la bonne police pour les boutons."""
        return self._draw_text(text, x, y, self.font, dry_run)
        
    def _draw_text(self, text, x, y, font, dry_run=False):
        """Méthode de rendu de texte générique."""
        surface = font.render(text, True, (255, 255, 255))
        width, height = surface.get_size()
        if dry_run: return width, height
        texture_data = pygame.image.tostring(surface, "RGBA", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 0); glVertex2f(x, y + height)
        glEnd()
        
        # --- CORRECTION ---
        # On s'assure de passer un entier Python standard à la fonction de suppression.
        glDeleteTextures(int(texture_id))
