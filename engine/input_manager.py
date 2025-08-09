# engine/input_manager.py

import pygame

class InputManager:
    """
    Gère toutes les entrées du joueur, y compris le clavier et la souris.
    """
    def __init__(self):
        self.movement_vector = [0, 0]
        self.mouse_delta = [0, 0]

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        # --- GESTION DE LA SOURIS ---
        self.mouse_pressed = False
        self._prev_mouse_pressed = False

        # --- CORRECTION DE LA GESTION DES TOUCHES ---
        # On initialise l'état actuel et précédent des touches.
        self.keys = pygame.key.get_pressed()
        self.prev_keys = self.keys

        # --- GESTION DES TOUCHES SPÉCIFIQUES (POUR LE DÉFILEMENT D'INVENTAIRE) ---
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
        self._prev_left = False
        self._prev_right = False
        self._prev_up = False
        self._prev_down = False

    def update(self):
        """
        Méthode appelée à chaque frame pour mettre à jour l'état de toutes les entrées.
        """
        # --- MISE À JOUR SOURIS ---
        self._prev_mouse_pressed = self.mouse_pressed
        self.mouse_pressed = pygame.mouse.get_pressed()[0]

        # --- CORRECTION DE LA GESTION DES TOUCHES ---
        # L'état de la frame précédente devient l'ancien état.
        self.prev_keys = self.keys
        # On récupère le nouvel état de toutes les touches.
        self.keys = pygame.key.get_pressed()

        # --- MISE À JOUR TOUCHES SPÉCIFIQUES ---
        self._prev_left = self.left_pressed
        self._prev_right = self.right_pressed
        self._prev_up = self.up_pressed
        self._prev_down = self.down_pressed

        self.left_pressed = self.keys[pygame.K_LEFT]
        self.right_pressed = self.keys[pygame.K_RIGHT]
        self.up_pressed = self.keys[pygame.K_UP]
        self.down_pressed = self.keys[pygame.K_DOWN]

        # --- MISE À JOUR MOUVEMENT ZQSD ---
        self.movement_vector = [0, 0]
        if self.keys[pygame.K_z]: self.movement_vector[1] += 1
        if self.keys[pygame.K_s]: self.movement_vector[1] -= 1
        if self.keys[pygame.K_q]: self.movement_vector[0] -= 1
        if self.keys[pygame.K_d]: self.movement_vector[0] += 1

        # --- MISE À JOUR POSITION SOURIS ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        center_x, center_y = pygame.display.get_surface().get_size()
        center_x //= 2
        center_y //= 2
        self.mouse_delta = [mouse_x - center_x, mouse_y - center_y]
        pygame.mouse.set_pos((center_x, center_y))

    def get_movement_vector(self):
        return self.movement_vector

    def get_mouse_delta(self):
        return self.mouse_delta

    def is_mouse_clicked(self):
        return self.mouse_pressed and not self._prev_mouse_pressed

    def is_mouse_held(self):
        return self.mouse_pressed
    
    def is_key_pressed(self, key):
        """Retourne True si la touche est actuellement enfoncée."""
        return self.keys[key]

    # --- NOUVELLE MÉTHODE CORRIGÉE ---
    def is_key_just_pressed(self, key):
        """Retourne True seulement à la frame où la touche est pressée."""
        return self.keys[key] and not self.prev_keys[key]

    def is_left_pressed(self):
        return self.left_pressed and not self._prev_left

    def is_right_pressed(self):
        return self.right_pressed and not self._prev_right

    def is_up_pressed(self):
        return self.up_pressed and not self._prev_up

    def is_down_pressed(self):
        return self.down_pressed and not self._prev_down
