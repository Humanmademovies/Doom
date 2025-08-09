# engine/game_engine.py

import pygame
from engine.input_manager import InputManager
from engine.renderer import Renderer
from world.map import GameMap
from objects.player import Player
from config import TARGET_FPS, DEFAULT_MAP

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        # running est maintenant utilisé pour indiquer à l'état parent de se fermer
        self.running = True

        # Composants du moteur
        self.input_manager = InputManager()
        self.renderer = Renderer(self.screen)
        self.game_map = GameMap()

        # Entités du jeu
        self.pnjs = []
        self.items = []

        # Chargement des ressources et placement du joueur
        self.load_resources()
        spawn_pos = self._find_free_cell()
        self.player = Player(position=[spawn_pos[0] + 0.5, 0.5, -spawn_pos[1] - 0.5])

    def load_resources(self):
        """Charge la carte, les textures et initialise les entités du niveau."""
        self.game_map.load_from_file(DEFAULT_MAP)
        self.pnjs = self.game_map.get_initial_pnjs()
        self.items = self.game_map.get_initial_items()
        self.renderer.load_textures()

    def update(self, delta_time):
        """
        Mise à jour, qui peut maintenant retourner une action comme "PAUSE".
        """
        # La boucle for event parcourt tous les événements en attente
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None # On quitte
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "REQUEST_PAUSE" # On envoie un signal

            # Ce bloc a été indenté pour être à l'intérieur de la boucle for
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Molette vers le haut
                    self.player.scroll_weapons(-1)
                elif event.button == 5:  # Molette vers le bas
                    self.player.scroll_weapons(1)

        # 1. Mise à jour des entrées utilisateur
        self.input_manager.update()

        # 2. Gestion des actions du joueur
        if self.input_manager.is_up_pressed(): self.player.scroll_items(-1)
        if self.input_manager.is_down_pressed(): self.player.scroll_items(1)
        
        if self.input_manager.is_key_just_pressed(pygame.K_SPACE): self.player.use_selected_item()
        if self.input_manager.is_key_pressed(pygame.K_r): self.player.reload_weapon()

        # 3. Mise à jour du joueur
        move_vector = self.input_manager.get_movement_vector()
        mouse_delta = self.input_manager.get_mouse_delta()
        self.player.update(move_vector, mouse_delta, delta_time, self.game_map)

        # 4. Logique de tir
        if self.input_manager.is_mouse_held():
            self.player.fire(self.pnjs, self.game_map)

        # 5. Mise à jour des PNJ et items
        for pnj in self.pnjs: pnj.update(self.player, delta_time, self.game_map, self.renderer)
        for item in self.items: item.update(self.player, delta_time)

        # Si aucune action spéciale n'est retournée, on retourne None par défaut
        return None

    def render(self):
        """Gère tout le rendu graphique."""
        self.renderer.clear()
        self.renderer.render_player(self.player)
        self.renderer.render_world(self.game_map)
        self.renderer.render_pnjs(self.pnjs)
        self.renderer.render_entities(self.items)
        self.renderer.render_hud(self.player, self.pnjs, self.items, self.game_map)
        self.renderer.swap_buffers()

    def _find_free_cell(self):
        """Trouve une case de sol libre pour faire apparaître le joueur."""
        for y, row in enumerate(self.game_map.grid):
            for x, cell in enumerate(row):
                if cell in self.game_map.floor_textures:
                    return (x, y)
        return (1, 1) # Fallback
