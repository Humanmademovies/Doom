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
        self.clock = pygame.time.Clock()
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
        MODIFIÉ: Cœur de la logique de jeu, mis à jour à chaque frame.
        """
        # 1. Mise à jour des entrées utilisateur
        self.input_manager.update()

        # 2. Gestion des actions du joueur (inventaire, rechargement)
        if self.input_manager.is_up_pressed():
            self.player.scroll_items(-1)
        if self.input_manager.is_down_pressed():
            self.player.scroll_items(1)
        if self.input_manager.is_left_pressed():
            self.player.scroll_weapons(-1)
        if self.input_manager.is_right_pressed():
            self.player.scroll_weapons(1)
        if self.input_manager.is_key_pressed(pygame.K_SPACE):
            self.player.use_selected_item()
            
        # NOUVEAU: Ajout de la touche 'R' pour recharger
        if self.input_manager.is_key_pressed(pygame.K_r):
            self.player.reload_weapon()

        # 3. Mise à jour de la position et de l'état du joueur
        move_vector = self.input_manager.get_movement_vector()
        mouse_delta = self.input_manager.get_mouse_delta()
        self.player.update(move_vector, mouse_delta, delta_time, self.game_map)

        # 4. NOUVELLE LOGIQUE DE TIR
        # Si la souris est maintenue, on tente de tirer.
        # La logique dans Player/Weapon gère la cadence et les munitions.
        if self.input_manager.is_mouse_held():
            self.player.fire(self.pnjs, self.game_map)

        # 5. Mise à jour des PNJ et des items
        for pnj in self.pnjs:
            pnj.update(self.player, delta_time, self.game_map, self.renderer)
        for item in self.items:
            # On passe delta_time à l'update de l'item au cas où on voudrait
            # y ajouter des animations (ex: rotation sur place)
            item.update(self.player, delta_time)


    def render(self):
        """Gère tout le rendu graphique."""
        self.renderer.clear()
        self.renderer.render_player(self.player)
        self.renderer.render_world(self.game_map)
        self.renderer.render_pnjs(self.pnjs)
        self.renderer.render_entities(self.items)
        
        # CORRECTION: On passe tous les arguments nécessaires à la fonction render_hud
        self.renderer.render_hud(self.player, self.pnjs, self.items, self.game_map)
        
        self.renderer.swap_buffers()
        
    def _find_free_cell(self):
        """Trouve une case de sol libre pour faire apparaître le joueur."""
        for y, row in enumerate(self.game_map.grid):
            for x, cell in enumerate(row):
                if cell in self.game_map.floor_textures:
                    return (x, y)
        return (1, 1) # Fallback

    def run(self):
        """Boucle de jeu principale."""
        while self.running:
            delta_time = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False

            self.update(delta_time)
            self.render()
