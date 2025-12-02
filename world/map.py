# world/map.py

import json
import os
import pygame
from objects.foe import Foe
from objects.friend import Friend
from objects.item import Item
from .sprite_analyzer import find_logo_positions, LOGO_SIZE

class GameMap:
    def __init__(self):
        self.grid = []
        self.wall_textures = {}
        self.floor_textures = {}
        self.friend_positions = []
        self.foe_positions = []
        self.item_positions = []
        self.building_positions = []
        self.transition_points = []
        self.spawn_points = {} # NOUVEL ATTRIBUT
        self.current_map_path = None
        
        
    def load_from_file(self, filepath):
        self.current_map_path = filepath
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Carte introuvable : {filepath}")
        with open(filepath, 'r') as file:
            data = json.load(file)
            self.grid = data.get("map", [])
            self.wall_textures = data.get("wall_textures", {})
            self.floor_textures = data.get("floor_textures", {})
            self.friend_positions = data.get("friends", [])
            self.foe_positions = data.get("foes", [])
            self.item_positions = data.get("items", [])
            self.building_positions = data.get("buildings", [])
            self.spawn_points = data.get("spawn_points", {}) # NOUVELLE LIGNE
        
        self._process_buildings()

    def _process_buildings(self):
        """
        MODIFIÉ: Le masque de collision est maintenant généré en isolant uniquement les pixels
        du rectangle principal du bâtiment (couleur 180, 180, 180), excluant ainsi les logos.
        """
        self.transition_points = []
        processed_buildings = []

        BUILDING_COLOR = (180, 180, 180)

        for building_data in self.building_positions:
            sprite_path = building_data.get("sprite")
            if not sprite_path: continue

            full_sprite_path = f"assets/sprites/{sprite_path}"
            
            try:
                image = pygame.image.load(full_sprite_path).convert_alpha()
                width, height = image.get_size()
            except pygame.error:
                width, height, image = 0, 0, None

            building_data['texture_width'] = width
            building_data['texture_height'] = height

            if image:
                # Création d'une surface temporaire pour isoler le bâtiment
                building_only_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                
                # On ne copie que les pixels de la couleur du bâtiment
                for y in range(height):
                    for x in range(width):
                        if image.get_at((x, y)) == BUILDING_COLOR:
                            building_only_surface.set_at((x, y), (255, 255, 255, 255))
                
                # Le masque est généré à partir de cette surface épurée
                building_data['mask'] = pygame.mask.from_surface(building_only_surface)
            else:
                building_data['mask'] = None

            logo_positions = find_logo_positions(full_sprite_path)
            
            if logo_positions:
                for i, (logo_x, logo_y) in enumerate(logo_positions):
                    self.transition_points.append({
                        "position_on_map": (building_data['x'], building_data['y']),
                        "anchor_in_sprite": (logo_x + LOGO_SIZE / 2, logo_y + LOGO_SIZE / 2),
                        "target_map": building_data.get("target_map"),
                        "target_spawn_id": f"{building_data.get('target_spawn_id', 'spawn')}_{i}"
                    })
                building_data['anchor_x'] = sum(p[0] + LOGO_SIZE / 2 for p in logo_positions) / len(logo_positions)
                building_data['anchor_y'] = sum(p[1] + LOGO_SIZE / 2 for p in logo_positions) / len(logo_positions)
            else:
                building_data['anchor_x'] = width / 2
                building_data['anchor_y'] = height / 2
            
            processed_buildings.append(building_data)

        self.building_positions = processed_buildings

    def get_wall_geometry(self):
        geometry = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell in self.wall_textures:
                    texture = self.wall_textures[cell]
                    # Face avant
                    geometry.append({
                        "vertices": [(x, 0, -y), (x + 1, 0, -y), (x + 1, 1, -y), (x, 1, -y)],
                        "texture": texture
                    })
                    # Face arrière
                    geometry.append({
                        "vertices": [(x + 1, 0, -y - 1), (x, 0, -y - 1), (x, 1, -y - 1), (x + 1, 1, -y - 1)],
                        "texture": texture
                    })
                    # Face droite
                    geometry.append({
                        "vertices": [(x + 1, 0, -y), (x + 1, 0, -y - 1), (x + 1, 1, -y - 1), (x + 1, 1, -y)],
                        "texture": texture
                    })
                    # Face gauche
                    geometry.append({
                        "vertices": [(x, 0, -y - 1), (x, 0, -y), (x, 1, -y), (x, 1, -y - 1)],
                        "texture": texture
                    })
                    # Plafond
                    geometry.append({
                        "vertices": [(x, 1, -y), (x + 1, 1, -y), (x + 1, 1, -y - 1), (x, 1, -y - 1)],
                        "texture": texture
                    })
        return geometry

    def get_floor_geometry(self):
        geometry = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell in self.floor_textures:
                    geometry.append({
                        "vertices": self._generate_floor_quad(x, y),
                        "texture": self.floor_textures[cell]
                    })
        return geometry

    def _generate_floor_quad(self, x, y):
        return [
            (x, 0, -y),
            (x + 1, 0, -y),
            (x + 1, 0, -y - 1),
            (x, 0, -y - 1)
        ]

    def _find_nearest_valid_position(self, start_x, start_y):
        from collections import deque
        visited = set()
        queue = deque([(start_x, start_y)])
        while queue:
            x, y = queue.popleft()
            if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
                if self.grid[y][x] in self.floor_textures:
                    return x, y
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return start_x, start_y

    def get_initial_pnjs(self):
        pnjs = []
        for pos in self.foe_positions + self.friend_positions:
            name = pos.get("name")
            if not name:
                continue
            x_init, y_init = pos["x"], pos["y"]
            if self.grid[y_init][x_init] not in self.floor_textures:
                x_cell, y_cell = self._find_nearest_valid_position(x_init, y_init)
            else:
                x_cell, y_cell = x_init, y_init
            world_pos = (x_cell + 0.5, 0, -y_cell - 0.5)
            config_path = os.path.join("assets", "pnj", name, "config.json")
            with open(config_path, "r") as f:
                data = json.load(f)
            mode = data.get("mode", "friend")
            if mode == "friend":
                pnjs.append(Friend(name=name, position=world_pos))
            else:
                pnjs.append(Foe(name=name, position=world_pos))
        return pnjs

    def get_initial_items(self):
        items = []
        for pos in self.item_positions:
            if isinstance(pos, dict) and "x" in pos and "y" in pos and "type" in pos:
                original_x, original_y = pos["x"], pos["y"]
                if self.grid[original_y][original_x] not in self.floor_textures:
                    new_x, new_y = self._find_nearest_valid_position(original_x, original_y)
                else:
                    new_x, new_y = original_x, original_y
                item_type = pos["type"]
                if item_type == "weapon":
                    items.append(Item(
                        position=(new_x + 0.5, 0, -new_y - 0.5),
                        item_type="weapon",
                        weapon_attrs=pos.get("weapon_attrs")
                    ))
                else:
                    items.append(Item(
                        position=(new_x + 0.5, 0, -new_y - 0.5),
                        item_type=item_type,
                        effect=pos.get("effect")
                    ))
        return items
