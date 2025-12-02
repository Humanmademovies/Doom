# states/menu_state.py

import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLU import *

from states.base_state import BaseState
from ui.button import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class MenuState(BaseState):
    """
    Gère le menu principal du jeu avec un rendu OpenGL.
    """
    def __init__(self, manager, screen):
        super().__init__(manager)
        self.screen = screen
        
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        try:
            self.font = pygame.font.Font("assets/ui/PressStart2P-Regular.ttf", 24)
        except pygame.error:
            self.font = pygame.font.Font(None, 40)

        # --- Boutons ---
        self.buttons = []
        center_x = self.screen.get_width() / 2
        
        # Bouton 1 : Nouvelle Aventure (Session Vierge)
        btn_new = Button(x=center_x - 150, y=200, width=300, height=50, text="Nouvelle Partie", callback=self.start_new_game)
        
        # Bouton 2 : Charger (Depuis savegame_1.json)
        btn_load = Button(x=center_x - 150, y=280, width=300, height=50, text="Charger Partie", callback=self.load_save)
        
        # Bouton 3 : Sélection de Carte (Pour vos tests)
        btn_map = Button(x=center_x - 150, y=360, width=300, height=50, text="Choisir Niveau", callback=self.go_to_map_selection)
        
        # Bouton 4 : Quitter
        btn_quit = Button(x=center_x - 150, y=440, width=300, height=50, text="Quitter", callback=self.quit_game)
        
        self.buttons.extend([btn_new, btn_load, btn_map, btn_quit])
        
        self.background_texture = self._load_background_texture("assets/ui/menu_background.png")

    def _load_background_texture(self, path):
        try:
            surface = pygame.image.load(path)
            image_data = pygame.image.tostring(surface, "RGBA", True)
            width, height = surface.get_size()

            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            return texture_id
        except (FileNotFoundError, pygame.error):
            print(f"Image de fond non trouvée ou erreur: {path}. Utilisation d'une couleur unie.")
            return None

    def _draw_text(self, text, x, y, dry_run=False):
        """Dessine du texte dans un contexte OpenGL."""
        surface = self.font.render(text, True, (255, 255, 255))
        
        width, height = surface.get_size()
        
        if dry_run:
            return width, height

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

    def start_new_game(self):
        """Lance une nouvelle session de jeu."""
        self.manager.start_new_session(self.screen)

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def go_to_map_selection(self):
        """Restaure l'accès à l'écran de sélection de carte."""
        from states.map_selection_state import MapSelectionState
        self.manager.switch_state(MapSelectionState(self.manager, self.screen))

    def load_save(self):
        """Tente de charger la sauvegarde n°1."""
        if self.manager.load_game(1, self.screen):
            pass 
        else:
            print("Echec du chargement (fichier inexistant ?)")

    def update(self, delta_time):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            for button in self.buttons:
                button.handle_event(event)
        for button in self.buttons:
            button.update(mouse_pos)

    def render(self, screen):
        """Affiche le menu en utilisant OpenGL."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        glClear(GL_COLOR_BUFFER_BIT)
        
        if self.background_texture:
            glBindTexture(GL_TEXTURE_2D, self.background_texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0)
            glTexCoord2f(1, 0); glVertex2f(SCREEN_WIDTH, 0)
            glTexCoord2f(1, 1); glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
            glTexCoord2f(0, 1); glVertex2f(0, SCREEN_HEIGHT)
            glEnd()
        else:
            glClearColor(0.1, 0.1, 0.15, 1.0) 

        for button in self.buttons:
            button.draw(self._draw_text)
        
        pygame.display.flip()
