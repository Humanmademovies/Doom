from objects.pnj import PNJ
from ai.behavior import decide_action
import random
from math import floor

class Foe(PNJ):
    def __init__(self, name, position=(0, 0, 0)):
        super().__init__(name=name, position=position)
        self.patrol_points = [position]
        self.current_patrol_index = 0
        self.attack_timer = 0.0  # temps écoulé depuis la dernière attaque


    def update(self, player, delta_time, game_map, renderer):
        super().update(player, delta_time, game_map)

        if self.health <= 0 or self.state == "dmg":
            return  # ne rien faire si mort ou en train d'afficher l'effet de blessure

        action = decide_action(self, player)

        if action == "idle":
            pass

        elif action == "patrol":
            self._patrol(delta_time, game_map)

        elif action == "chase":
            self._move_toward(player.position, delta_time, game_map)

        elif action == "attack":
            self.attack_timer += delta_time
            cooldown = 1.0 - min(max(self.P, 0), 10) / 10.0
            if self.attack_timer >= cooldown and self.has_line_of_sight(player, game_map):
                self._attack(player, renderer)
                self.attack_timer = 0.0
            else:
                if self.state == "attack":
                    self.set_action("idle")

        # Appliquer l’état visuel si aucun effet n’est prioritaire
        if self.dmg_timer <= 0 and self.state != "dead":
            self.set_action(action)





    def _move_toward(self, target_pos, delta_time, game_map):
        dx = target_pos[0] - self.position[0]
        dz = target_pos[2] - self.position[2]
        dist = (dx**2 + dz**2) ** 0.5
        if dist < 0.01:
            return

        dir_x = dx / dist
        dir_z = dz / dist
        next_x = self.position[0] + dir_x * self.speed * delta_time
        next_z = self.position[2] + dir_z * self.speed * delta_time

        offset = 0.2

        cell_x = int(next_x + (offset if dir_x > 0 else -offset))
        cell_z = int(-self.position[2])
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]):
            if game_map.grid[cell_z][cell_x] in game_map.floor_textures:
                self.position = (next_x, self.position[1], self.position[2])

        cell_x = int(self.position[0])
        cell_z = int(-next_z + (offset if dir_z < 0 else -offset))
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]):
            if game_map.grid[cell_z][cell_x] in game_map.floor_textures:
                self.position = (self.position[0], self.position[1], next_z)

    def _attack(self, player, renderer):
        if self.health > 0 and player.health > 0:
            
            if random.random() <= min(max(self.S, 0), 10) / 10.0:
                player.take_damage(self.P)
                renderer.damage_overlay_timer = 0.1

            else:
                print(f"{self.sprite} rate son attaque.")
            


    def _patrol(self, delta_time, game_map):
        if not self.patrol_points:
            return

        target = self.patrol_points[self.current_patrol_index]
        dx = target[0] - self.position[0]
        dz = target[2] - self.position[2]
        dist = (dx**2 + dz**2) ** 0.5

        if dist < 0.1:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            return

        self._move_toward(target, delta_time, game_map)

    def has_line_of_sight(self, target, game_map):

        x0 = int(self.position[0])
        y0 = int(-self.position[2])  # axe Z inversé

        x1 = int(target.position[0])
        y1 = int(-target.position[2])

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while x != x1 or y != y1:
            if 0 <= y < len(game_map.grid) and 0 <= x < len(game_map.grid[0]):
                cell = game_map.grid[y][x]
                if cell not in game_map.floor_textures:
                    return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True
