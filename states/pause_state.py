# states/pause_state.py

import pygame
import sys
from OpenGL.GL import *

from states.base_state import BaseState
from ui.button import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT

# Pour éviter une boucle d'importation, on ne l'importe que pour le "type hinting"
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_state_manager import GameStateManager
    from states.menu_state import MenuState


class PauseState(BaseState):
    """
    Gère le menu de pause. S'affiche par-dessus l'état de jeu.
    """
    def __init__(self, manager: 'GameStateManager', screen):
        super().__init__(manager)
        self.screen = screen

        # On réactive la souris pour le menu
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        try:
            self.font = pygame.font.Font("assets/ui/PressStart2P-Regular.ttf", 24)
        except pygame.error:
            self.font = pygame.font.Font(None, 40)

        # Création des boutons
        self.buttons = []
        center_x = self.screen.get_width() / 2
        
        btn_reprendre = Button(
            x=center_x - 150, y=200, width=300, height=50,
            text="Reprendre", callback=self.resume_game
        )
        btn_sauver = Button(
            x=center_x - 150, y=280, width=300, height=50,
            text="Sauvegarder", callback=self.save_game
        )
        btn_charger = Button(
            x=center_x - 150, y=360, width=300, height=50,
            text="Charger", callback=self.load_game
        )
        btn_menu_principal = Button(
            x=center_x - 150, y=440, width=300, height=50,
            text="Menu Principal", callback=self.back_to_main_menu
        )
        self.buttons.extend([btn_reprendre, btn_sauver, btn_charger, btn_menu_principal])

    def resume_game(self):
        # On retire simplement l'état de pause de la pile pour revenir au jeu
        self.manager.pop_state()
        print("Jeu repris.")

    def save_game(self):
        # On appelle simplement la méthode de sauvegarde du manager
        self.manager.save_game(1)


    # dans states/pause_state.py

    def load_game(self):
        # On appelle la nouvelle méthode du manager
        self.manager.load_game(1)
        # Après le chargement, on veut souvent revenir directement au jeu
        self.resume_game()

    def back_to_main_menu(self):
        # On vide la pile et on retourne au menu principal
        from states.menu_state import MenuState
        self.manager.switch_state(MenuState(self.manager, self.screen))

    def update(self, delta_time):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # On permet aussi de quitter la pause avec Echap
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.resume_game()
                return # Important pour éviter de traiter d'autres événements

            for button in self.buttons:
                button.handle_event(event)

        for button in self.buttons:
            button.update(mouse_pos)

    # dans states/pause_state.py

    def render(self, screen):
        # On ne vide pas l'écran pour garder l'image du jeu en fond.
        
        # --- CONFIGURATION DU RENDU 2D ---
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # --- CORRECTION ---
        # On désactive le test de profondeur pour s'assurer que notre UI 2D
        # s'affiche toujours par-dessus la scène 3D.
        glDisable(GL_DEPTH_TEST)
        
        # On active la transparence pour l'effet d'assombrissement
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # On dessine le rectangle noir semi-transparent
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(SCREEN_WIDTH, 0)
        glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
        glVertex2f(0, SCREEN_HEIGHT)
        glEnd()
        
        # On dessine les boutons par-dessus le filtre
        for button in self.buttons:
            button.draw(self._draw_text)
        
        # On remet les états OpenGL propres pour la suite (bonne pratique)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        
        pygame.display.flip()
        
    def _draw_text(self, text, x, y, dry_run=False):
        """Méthode de rendu de texte (copiée de MenuState pour l'instant)."""
        surface = self.font.render(text, True, (255, 255, 255))
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
        glDeleteTextures(texture_id)
