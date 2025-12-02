# engine/game_engine.py

import pygame
from engine.input_manager import InputManager
from engine.renderer import Renderer
from world.map import GameMap
from objects.player import Player
from config import TARGET_FPS, DEFAULT_MAP



class GameEngine:
    def __init__(self, screen, map_path, spawn_id=None, game_session=None):
        self.screen = screen
        self.running = True
        self.map_path = map_path
        self.game_session = game_session 

        self.input_manager = InputManager()
        self.renderer = Renderer(self.screen)
        self.game_map = GameMap()

        self.pnjs = []
        self.items = []

        self.load_resources()
        
        spawn_pos = self._find_spawn_position(spawn_id)
        self.player = Player(position=[spawn_pos[0], 0.5, -spawn_pos[1]])


    def _find_spawn_position(self, spawn_id):
        """
        NOUVEAU: Cherche un point de spawn par ID dans la carte.
        S'il n'est pas trouvé, utilise le premier disponible ou un fallback.
        """
        spawn_points = self.game_map.spawn_points # On suppose que la carte charge un dict spawn_points
        
        if spawn_id and spawn_id in spawn_points:
            # Position trouvée par ID
            pos = spawn_points[spawn_id]
            return pos[0], pos[1]
        elif spawn_points:
            # Prend le premier point de spawn de la liste
            first_key = list(spawn_points.keys())[0]
            pos = spawn_points[first_key]
            return pos[0], pos[1]
        else:
            # Fallback si aucun point de spawn n'est défini
            print("AVERTISSEMENT: Aucun point de spawn trouvé, utilisation d'une position par défaut.")
            return self._find_free_cell()


    def _find_free_cell(self):
        """Trouve une case de sol libre pour faire apparaître le joueur."""
        for y, row in enumerate(self.game_map.grid):
            for x, cell in enumerate(row):
                if cell in self.game_map.floor_textures:
                    return (x + 0.5, y + 0.5) # Centré sur la tuile
        return (1.5, 1.5) # Fallback

    def load_resources(self):
        """Charge la carte, les textures et initialise les entités du niveau."""
        self.game_map.load_from_file(self.map_path) 
        self.pnjs = self.game_map.get_initial_pnjs(self.game_session)
        self.items = self.game_map.get_initial_items(self.game_session)
        self.renderer.load_textures()

    def update(self, delta_time):
        """
        Mise à jour, qui peut maintenant retourner une action comme "PAUSE" ou "GAME_OVER".
        """
        # Vérification de la mort du joueur en début de frame
        if self.player.health <= 0:
            return "GAME_OVER"

        # Gestion des événements Pygame (Fenêtre, Quitter, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None 
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "REQUEST_PAUSE" 

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.player.scroll_weapons(-1)
                elif event.button == 5:
                    self.player.scroll_weapons(1)

        # --- CORRECTION MAJEURE : On met à jour les inputs AVANT de tester la logique ---
        self.input_manager.update()

        # Interaction avec l'environnement (Portes) - SCAN ROBUSTE
        if self.input_manager.is_key_just_pressed(pygame.K_e):
            import math
            
            # CORRECTION VECTORIELLE (0° = -Z)
            rad = math.radians(-self.player.rotation_y)
            dir_x = math.sin(rad)
            dir_z = -math.cos(rad)
            
            check_distances = [0.5, 0.75, 1.0, 1.25, 1.5]
            
            found_interaction = False
            for dist in check_distances:
                if found_interaction: break

                target_x = self.player.position[0] + dir_x * dist
                target_z = self.player.position[2] + dir_z * dist
                
                check_x = int(target_x)
                check_y = int(-target_z)
                
                if 0 <= check_y < len(self.game_map.grid) and 0 <= check_x < len(self.game_map.grid[0]):
                    cell_value = self.game_map.grid[check_y][check_x]
                    
                    if hasattr(self.game_map, 'doors_config') and cell_value in self.game_map.doors_config:
                        door_data = self.game_map.doors_config[cell_value]
                        print(f"!!! PORTE ACTIVÉE (Distance {dist}m) !!! Vers {door_data['target_map']}")
                        return {"type": "EXIT_TO_MAP", "target": door_data["target_map"]}
                    
                    elif cell_value != "0.1": 
                        found_interaction = True

        # 2. Gestion des actions du joueur (Inventaire, etc.)
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
        for pnj in self.pnjs: 
            pnj.update(self.player, delta_time, self.game_map, self.renderer)
            
            if pnj.health <= 0:
                if self.game_session and not self.game_session.is_flagged(self.map_path, "killed", pnj.id):
                    self.game_session.register_action(self.map_path, "killed", pnj.id)
                    print(f"[PERSISTANCE] Mort enregistrée : {pnj.id}")

        for item in self.items: 
            was_collected = item.collected
            item.update(self.player, delta_time)
            
            # Si l'item vient d'être ramassé
            if not was_collected and item.collected:
                if self.game_session:
                    self.game_session.register_action(self.map_path, "collected", item.id)
                    print(f"[PERSISTANCE] Ramassage enregistré : {item.id}")

        # 6. Vérification des sorties automatiques (Rétrocompatibilité 'exits')
        if hasattr(self.game_map, 'exits'):
            for exit_point in self.game_map.exits:
                exit_world_x = exit_point["x"] + 0.5
                exit_world_z = -(exit_point["y"] + 0.5)
                dx = self.player.position[0] - exit_world_x
                dz = self.player.position[2] - exit_world_z
                if (dx**2 + dz**2) ** 0.5 < 0.5:
                    return {"type": "EXIT_TO_MAP", "target": exit_point["target_map"]}

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


   
