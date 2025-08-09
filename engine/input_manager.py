# engine/input_manager.py

import pygame

class InputManager:
    """
    Gère toutes les entrées du joueur, y compris le clavier et la souris.
    Cette classe abstrait les événements Pygame pour fournir des méthodes simples
    et claires à utiliser dans le moteur de jeu (ex: "le joueur avance ?", 
    "la souris a-t-elle été cliquée ?").
    """
    def __init__(self):
        self.movement_vector = [0, 0]  # [strafe (gauche/droite), forward (avant/arrière)]
        self.mouse_delta = [0, 0]

        # --- GESTION DE LA SOURIS ---
        pygame.event.set_grab(True)      # La souris est capturée par la fenêtre
        pygame.mouse.set_visible(False)  # La souris est invisible

        # État actuel du bouton gauche de la souris (True si pressé)
        self.mouse_pressed = False
        
        # NOUVEAU: Stocke l'état de la souris de la frame précédente.
        # C'est la clé pour détecter un "clic" (un seul événement) par opposition 
        # à un "appui maintenu".
        self._prev_mouse_pressed = False

        # --- GESTION DES TOUCHES (POUR LE DÉFILEMENT D'INVENTAIRE) ---
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
        # Stockage de l'état précédent des touches pour détecter un appui unique
        self._prev_left = False
        self._prev_right = False
        self._prev_up = False
        self._prev_down = False


    def update(self):
        """
        Méthode appelée à chaque frame pour mettre à jour l'état de toutes les entrées.
        """
        # --- MISE À JOUR SOURIS ---
        # NOUVEAU: On sauvegarde l'état du clic de la frame d'avant
        self._prev_mouse_pressed = self.mouse_pressed
        # On récupère le nouvel état du clic gauche
        self.mouse_pressed = pygame.mouse.get_pressed()[0]

        # --- MISE À JOUR TOUCHES DIRECTIONNELLES (POUR INVENTAIRE) ---
        keys = pygame.key.get_pressed()
        self._prev_left = self.left_pressed
        self._prev_right = self.right_pressed
        self._prev_up = self.up_pressed
        self._prev_down = self.down_pressed

        self.left_pressed = keys[pygame.K_LEFT]
        self.right_pressed = keys[pygame.K_RIGHT]
        self.up_pressed = keys[pygame.K_UP]
        self.down_pressed = keys[pygame.K_DOWN]

        # --- MISE À JOUR MOUVEMENT ZQSD ---
        self.movement_vector = [0, 0]
        if keys[pygame.K_z]:
            self.movement_vector[1] += 1  # Avancer
        if keys[pygame.K_s]:
            self.movement_vector[1] -= 1  # Reculer
        if keys[pygame.K_q]:
            self.movement_vector[0] -= 1  # Strafe gauche
        if keys[pygame.K_d]:
            self.movement_vector[0] += 1  # Strafe droite

        # --- MISE À JOUR POSITION SOURIS (ROTATION CAMÉRA) ---
        # Calcul du mouvement relatif de la souris depuis le centre de l'écran
        mouse_x, mouse_y = pygame.mouse.get_pos()
        center_x, center_y = pygame.display.get_surface().get_size()
        center_x //= 2
        center_y //= 2
        self.mouse_delta = [mouse_x - center_x, mouse_y - center_y]
        
        # On replace la souris au centre pour le prochain calcul de delta
        pygame.mouse.set_pos((center_x, center_y))

    # --- MÉTHODES D'ACCÈS (GETTERS) ---

    def get_movement_vector(self):
        return self.movement_vector

    def get_mouse_delta(self):
        return self.mouse_delta

    # --- NOUVELLES MÉTHODES POUR LA GESTION DU TIR ---

    def is_mouse_clicked(self):
        """
        NOUVEAU: Renvoie True seulement à la frame exacte où le bouton est pressé.
        (Détection de "flanc montant")
        Idéal pour les actions uniques comme le tir semi-automatique.
        """
        return self.mouse_pressed and not self._prev_mouse_pressed

    def is_mouse_held(self):
        """
        MODIFIÉ: Renvoie True tant que le bouton de la souris est maintenu enfoncé.
        (Anciennement is_mouse_pressed)
        Idéal pour les actions continues comme le tir automatique.
        """
        return self.mouse_pressed
    
    def is_key_pressed(self, key):
        return pygame.key.get_pressed()[key]

    # --- MÉTHODES POUR DÉTECTER UN APPUI UNIQUE SUR LES TOUCHES ---

    def is_left_pressed(self):
        return self.left_pressed and not self._prev_left

    def is_right_pressed(self):
        return self.right_pressed and not self._prev_right

    def is_up_pressed(self):
        return self.up_pressed and not self._prev_up

    def is_down_pressed(self):
        return self.down_pressed and not self._prev_down
