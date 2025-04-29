# objects/enemy.py

from objects.game_object import GameObject
from ai.behavior import decide_action

class Enemy(GameObject):
    def __init__(self, position=(0.0, 0.0, 0.0), enemy_type="basic"):
        super().__init__(position)
        self.enemy_type = enemy_type
        self.state = "idle"
        self.health = 50
        self.speed = 2.0
        self.rotation_y = 0.0

        # Patrouille : points de passage
        self.patrol_points = [
            (position[0], position[1], position[2]),
            (position[0] + 3.0, position[1], position[2]),
            (position[0], position[1], position[2] + 3.0)
        ]
        self.current_patrol_index = 0

    def update(self, player, delta_time, game_map):

        if self.health <= 0:
            self.state = "dead"
            self.visible = False
            return

        action = decide_action(self, player)
        if action == "chase":
            self._move_toward(player.position, delta_time, game_map)
        elif action == "attack":
            self._attack(player)
        elif action == "patrol":
            self._patrol(delta_time)
        elif action == "idle":
            pass

    def draw(self, renderer):
        if self.visible:
            renderer.draw_sprite(self.position, texture_name=f"{self.enemy_type}.png")

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.state = "dead"
            self.visible = False

    def _move_toward(self, target_pos, delta_time, game_map=None):
        dx = target_pos[0] - self.position[0]
        dz = target_pos[2] - self.position[2]
        dist = (dx**2 + dz**2) ** 0.5
        if dist < 0.01:
            return

        dir_x = dx / dist
        dir_z = dz / dist
        next_x = self.position[0] + dir_x * self.speed * delta_time
        next_z = self.position[2] + dir_z * self.speed * delta_time

        # Collision simple avec murs
        offset = 0.2

        # X
        cell_x = int(next_x + (offset if dir_x > 0 else -offset))
        cell_z = int(-self.position[2])
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]):
            if game_map.grid[cell_z][cell_x] in game_map.floor_textures:
                self.position[0] = next_x

        # Z
        cell_x = int(self.position[0])
        cell_z = int(-next_z + (offset if dir_z < 0 else -offset))
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]):
            if game_map.grid[cell_z][cell_x] in game_map.floor_textures:
                self.position[2] = next_z


    def _attack(self, player):
        player.health -= 5
        print(f"{self.enemy_type} attaque le joueur. Santé : {player.health}")

    def _patrol(self, delta_time):
        if not self.patrol_points:
            return

        target = self.patrol_points[self.current_patrol_index]
        arrived = self._move_toward(target, delta_time)
        if arrived:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
