# world/level_generator.py

import random
import json

class LevelGenerator:
    def __init__(self, width=21, height=21):
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]  # 1 = mur

    def generate_maze(self):
        def carve(x, y):
            dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1:
                    if self.grid[ny][nx] == 1:
                        self.grid[ny][nx] = 0
                        self.grid[y + dy // 2][x + dx // 2] = 0
                        carve(nx, ny)

        self.grid[1][1] = 0
        carve(1, 1)

    def place_enemies(self, count):
        positions = []
        candidates = [(x, y) for y in range(self.height) for x in range(self.width) if self.grid[y][x] == 0]
        for _ in range(count):
            if not candidates:
                break
            pos = random.choice(candidates)
            candidates.remove(pos)
            positions.append({"x": pos[0], "y": pos[1]})
        return positions

    def place_items(self, count):
        types = ["potion", "key", "ammo"]
        positions = []
        candidates = [(x, y) for y in range(self.height) for x in range(self.width) if self.grid[y][x] == 0]
        for _ in range(count):
            if not candidates:
                break
            pos = random.choice(candidates)
            item_type = random.choice(types)
            candidates.remove(pos)
            positions.append({"x": pos[0], "y": pos[1], "type": item_type})
        return positions

    def export_to_json(self, path, wall_texture_id=1, floor_texture_id=0.1):
        data = {
            "map": [
                [wall_texture_id if cell == 1 else floor_texture_id for cell in row]
                for row in self.grid
            ],
            "wall_textures": {str(wall_texture_id): "stone_wall.png"},
            "floor_textures": {str(floor_texture_id): "stone_floor.png"},
            "enemies": self.place_enemies(5),
            "items": self.place_items(3)
        }

        with open(path, 'w') as file:
            json.dump(data, file, indent=4)

# Exemple d'utilisation (à exécuter en script autonome si besoin) :
if __name__ == "__main__":
    gen = LevelGenerator(21, 21)
    gen.generate_maze()
    gen.export_to_json("assets/maps/generated_map.json")
