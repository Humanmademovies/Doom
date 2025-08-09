# states/menu_state.py

import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLU import *

from states.base_state import BaseState
from states.interior_state import InteriorState
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
        new_game_button = Button(
            x=center_x - 150, y=300, width=300, height=50,
            text="Nouvelle Partie", callback=self.start_new_game
        )
        quit_button = Button(
            x=center_x - 150, y=400, width=300, height=50,
            text="Quitter", callback=self.quit_game
        )
        self.buttons.extend([new_game_button, quit_button])
        
        # (Optionnel) Chargement de la texture de fond
        self.background_texture = self._load_background_texture("assets/ui/menu_background.png")

    # dans states/menu_state.py

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
        # --- CORRECTION ICI ---
        # On attrape la bonne exception : FileNotFoundError
        except FileNotFoundError:
            print(f"Image de fond non trouvée à {path}. Utilisation d'une couleur unie.")
            return None

    def _draw_text(self, text, x, y, dry_run=False):
        """Dessine du texte dans un contexte OpenGL."""
        # --- CORRECTION ICI ---
        # La méthode self.font.render() ne retourne qu'une surface, pas un tuple.
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
        
        glDeleteTextures(texture_id)

    def start_new_game(self):
        """Passe à l'écran de sélection de la carte."""
        from states.map_selection_state import MapSelectionState # Import local
        next_state = MapSelectionState(self.manager, self.screen)
        self.manager.switch_state(next_state)

    def quit_game(self):
        pygame.quit()
        sys.exit()

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
        # Configuration de la vue 2D
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        # Efface l'écran
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Dessine l'arrière-plan
        if self.background_texture:
            glBindTexture(GL_TEXTURE_2D, self.background_texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0)
            glTexCoord2f(1, 0); glVertex2f(SCREEN_WIDTH, 0)
            glTexCoord2f(1, 1); glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
            glTexCoord2f(0, 1); glVertex2f(0, SCREEN_HEIGHT)
            glEnd()
        else:
            glClearColor(0.1, 0.1, 0.15, 1.0) # Couleur de fond si pas d'image

        # Dessine les boutons
        for button in self.buttons:
            button.draw(self._draw_text)
        
        pygame.display.flip()
