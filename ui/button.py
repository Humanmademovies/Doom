# ui/button.py

import pygame
from OpenGL.GL import *

class Button:
    """
    Classe pour les boutons, mise à jour pour un rendu OpenGL.
    """
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback

        self.color = (0.2, 0.2, 0.25, 1.0)        # Couleur RGBA (50, 50, 64)
        self.hover_color = (0.4, 0.4, 0.45, 1.0)  # Couleur RGBA (100, 100, 115)
        self.is_hovered = False

    def handle_event(self, event):
        """Gère les événements de la souris (clic)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def update(self, mouse_pos):
        """Met à jour l'état de survol."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, draw_text_func):
        """
        Dessine le bouton en utilisant des commandes OpenGL.
        Nécessite une fonction externe pour dessiner le texte.
        """
        # Choisit la couleur en fonction du survol
        color = self.hover_color if self.is_hovered else self.color
        glColor4f(*color)

        # Dessine le rectangle du bouton
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glVertex2f(self.rect.left, self.rect.top)
        glVertex2f(self.rect.right, self.rect.top)
        glVertex2f(self.rect.right, self.rect.bottom)
        glVertex2f(self.rect.left, self.rect.bottom)
        glEnd()
        glEnable(GL_TEXTURE_2D)

        # Calcule la position du texte pour le centrer
        text_width, text_height = draw_text_func(self.text, 0, 0, dry_run=True)
        text_x = self.rect.centerx - text_width / 2
        text_y = self.rect.centery - text_height / 2
        
        # Dessine le texte par-dessus
        draw_text_func(self.text, text_x, text_y)
