# engine/input_manager.py

import pygame

class InputManager:
    def __init__(self):
        self.movement_vector = [0, 0]  # [gauche/droite, avant/arrière]
        self.mouse_delta = [0, 0]
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self._last_mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = False

        # État des flèches ← →
        self.left_pressed = False
        self.right_pressed = False
        self._prev_left = False
        self._prev_right = False

    def update(self):
        keys = pygame.key.get_pressed()

        # Détection de clic pour les flèches gauche/droite
        self._prev_left = self.left_pressed
        self._prev_right = self.right_pressed
        self.left_pressed = keys[pygame.K_LEFT] and not self._prev_left
        self.right_pressed = keys[pygame.K_RIGHT] and not self._prev_right

        self.movement_vector = [0, 0]
        if keys[pygame.K_z]:
            self.movement_vector[1] += 1  # avancer
        if keys[pygame.K_s]:
            self.movement_vector[1] -= 1  # reculer
        if keys[pygame.K_q]:
            self.movement_vector[0] -= 1  # gauche
        if keys[pygame.K_d]:
            self.movement_vector[0] += 1  # droite

        # Souris : calcul du delta
        mouse_x, mouse_y = pygame.mouse.get_pos()
        center_x, center_y = pygame.display.get_surface().get_size()
        center_x //= 2
        center_y //= 2
        self.mouse_delta = [mouse_x - center_x, mouse_y - center_y]
        pygame.mouse.set_pos((center_x, center_y))
        self.mouse_pressed = pygame.mouse.get_pressed()[0]

    def get_movement_vector(self):
        return self.movement_vector

    def get_mouse_delta(self):
        return self.mouse_delta

    def is_mouse_pressed(self):
        return self.mouse_pressed

    def is_left_pressed(self):
        return self.left_pressed

    def is_right_pressed(self):
        return self.right_pressed
    
    def is_key_pressed(self, key):
        return pygame.key.get_pressed()[key]
