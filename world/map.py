# world/map.py

import json
import os
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

        self._load_building_transitions()

    def _load_building_transitions(self):
        self.transition_points = []
        for building_data in self.building_positions:
            sprite_path = building_data.get("sprite")
            if not sprite_path:
                continue

            logo_positions = find_logo_positions(f"assets/sprites/{sprite_path}")
            
            if logo_positions:
                total_x = sum(p[0] for p in logo_positions)
                total_y = sum(p[1] for p in logo_positions)
                center_x = total_x / len(logo_positions)
                center_y = total_y / len(logo_positions)
                
                world_x = building_data["x"] + center_x / LOGO_SIZE
                world_y = building_data["y"] + center_y / LOGO_SIZE

                self.transition_points.append({
                    "position": (world_x, world_y),
                    "target_map": building_data.get("target_map"),
                    "target_spawn_id": building_data.get("target_spawn_id")
                })
        print(f"Points de transition détectés : {self.transition_points}")

    def get_wall_geometry(self):
        geometry = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell in self.wall_textures:
                    if cell in self.wall_textures:
                        texture = self.wall_textures[cell]
                        geometry.append({
                            "vertices": [
                                (x, 0, -y),
                                (x + 1, 0, -y),
                                (x + 1, 1, -y),
                                (x, 1, -y)
                            ],
                            "texture": texture
                        })
                        geometry.append({
                            "vertices": [
                                (x + 1, 0, -y - 1),
                                (x, 0, -y - 1),
                                (x, 1, -y - 1),
                                (x + 1, 1, -y - 1)
                            ],
                            "texture": texture
                        })
                        geometry.append({
                            "vertices": [
                                (x + 1, 0, -y),
                                (x + 1, 0, -y - 1),
                                (x + 1, 1, -y - 1),
                                (x + 1, 1, -y)
                            ],
                            "texture": texture
                        })
                        geometry.append({
                            "vertices": [
                                (x, 0, -y - 1),
                                (x, 0, -y),
                                (x, 1, -y),
                                (x, 1, -y - 1)
                            ],
                            "texture": texture
                        })
                        geometry.append({
                            "vertices": [
                                (x, 1, -y),
                                (x + 1, 1, -y),
                                (x + 1, 1, -y - 1),
                                (x, 1, -y - 1)
                            ],
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

    def _generate_wall_quad(self, x, y):
        return [
        (x, 0, -y),
        (x + 1, 0, -y),
        (x + 1, 1, -y),
        (x, 1, -y)
    ]


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
        queue = deque()
        queue.append((start_x, start_y))
        while queue:
            x, y = queue.popleft()
            if (0 <= y < len(self.grid)) and (0 <= x < len(self.grid[0])):
                if self.grid[y][x] in self.floor_textures:
                    return x, y
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
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
