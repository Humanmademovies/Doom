# objects/player.py

from objects.game_object import GameObject
from config import PLAYER_SPEED, MOUSE_SENSITIVITY
import math
from objects.weapon import Weapon

class Player(GameObject):
    def __init__(self, position=(1.0, 0.0, 1.0)):
        super().__init__(position)
        self.health = 100
        self.inventory_items = []
        self.inventory_weapons = []
        self.item_index = 0
        self.weapon_index = 0
        self.level = 1
        self.rotation_y = 0.0
        self.active_weapon = Weapon(name="fist", weapon_type="melee")
        self.attack_timer = 0.0
        self.can_attack = True

    def _is_in_view(self, target, fov=60.0):
        dx = target.position[0] - self.position[0]
        dz = target.position[2] - self.position[2]

        # Caméra regarde vers -Z → atan2(-dx, -dz) = 0° droit devant
        angle_to_target = (math.degrees(math.atan2(-dx, -dz))) % 360
        player_angle = self.rotation_y % 360
        diff = (angle_to_target - player_angle + 180) % 360 - 180
        in_view = abs(diff) <= (fov / 2)

        print(f"[ANGLE TEST] target={target.name}, angle_to_target={angle_to_target:.1f}°, player_angle={player_angle:.1f}°, diff={diff:.1f}°, in_view={in_view}")
        return in_view

    def _has_line_of_sight(self, target, game_map):
        x0 = int(self.position[0])
        y0 = int(-self.position[2])
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
                if game_map.grid[y][x] not in game_map.floor_textures:
                    return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        return True


    def update(self, movement_vector, mouse_delta, delta_time, game_map):

        dx, dz = 0.0, 0.0
        forward, strafe = movement_vector

        rad = math.radians(-self.rotation_y)
        sin_y, cos_y = math.sin(rad), math.cos(rad)

        self.rotation_y -= mouse_delta[0] * MOUSE_SENSITIVITY
        self.rotation_y %= 360

        speed_boost = getattr(self, "_tmp_speed_value", None)
        if speed_boost is None:
            speed_boost = PLAYER_SPEED




        dx += forward * cos_y * speed_boost * delta_time
        dz += forward * sin_y * speed_boost * delta_time
        dx += strafe * sin_y * speed_boost * delta_time
        dz -= strafe * cos_y * speed_boost * delta_time


        offset = 0.2

        # Tentative de déplacement en X
        next_x = self.position[0] + dx
        cell_x = int(next_x + (offset if dx > 0 else -offset))
        cell_z = int(-self.position[2])
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]):
            if game_map.grid[cell_z][cell_x] in game_map.floor_textures:
                self.position[0] = next_x

        # Tentative de déplacement en Z
        next_z = self.position[2] + dz
        cell_x = int(self.position[0])
        cell_z = int(-next_z + (offset if dz < 0 else -offset))
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]):
            if game_map.grid[cell_z][cell_x] in game_map.floor_textures:
                self.position[2] = next_z
        
        if not self.can_attack:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.set_weapon_state("idle")
                self.can_attack = True

                # ---------- GESTION DES EFFETS TEMPORAIRES ----------
        for attr in ["speed", "resist", "invincible"]:
            timer = getattr(self, f"_tmp_{attr}_timer", 0)
            if timer > 0:
                timer -= delta_time
                setattr(self, f"_tmp_{attr}_timer", timer)
                if timer <= 0:
                    setattr(self, f"_tmp_{attr}_value", None)
                    print(f"Effet temporaire terminé : {attr}")

    def draw(self, renderer):
        pass  # Vue subjective, pas de rendu direct

    # ---------- INVENTAIRE & OBJETS ----------

    def add_to_inventory(self, item):
        if item.item_type == "weapon":
            self.inventory_weapons.append(item)
            self.weapon_index = len(self.inventory_weapons) - 1  # sélection auto
        else:
            self.inventory_items.append(item)
            self.item_index = len(self.inventory_items) - 1  # sélection auto

    def scroll_items(self, direction):
        if not self.inventory_items:
            self.item_index = 0
            return
        self.item_index = (self.item_index + direction) % len(self.inventory_items)

    def scroll_weapons(self, direction):
        if not self.inventory_weapons:
            self.weapon_index = 0
            return
        self.weapon_index = (self.weapon_index + direction) % len(self.inventory_weapons)
        self.equip(self.get_selected_weapon())

    def equip(self, weapon):
        self.active_weapon = weapon

    def fire(self):
        if self.active_weapon:
            self.active_weapon.fire(from_position=self.position, direction=self.rotation_y)

    # ---------- INTERACTION AVEC OBJETS DU MONDE ----------

    def interact(self, target):
        if hasattr(target, "on_interact"):
            target.on_interact(self)

    def switch_weapon(self, name, weapon_type):
        self.active_weapon = Weapon(name, weapon_type)

    def set_weapon_state(self, state):
        self.active_weapon.set_state(state)

    def perform_attack(self, pnjs, game_map):
        if not self.can_attack or self.health <= 0:
            return
        
        self.set_weapon_state("attack")
        self.attack_timer = 0.3  # durée fixe d'animation d'attaque
        self.can_attack = False
        weapon = self.active_weapon
        targets = []


        targets = []
        for pnj in pnjs:
            if hasattr(pnj, "health") and pnj.health > 0:
                dx = pnj.position[0] - self.position[0]
                dz = self.position[2] - pnj.position[2]
                distance = (dx**2 + dz**2) ** 0.5
   

                if self._is_in_view(pnj) and self._has_line_of_sight(pnj, game_map):
                    targets.append((distance, pnj))

        print(f"{len(targets)} cibles visibles sur {len(pnjs)} PNJ")

        if weapon.weapon_type == "melee":
            if targets:
                target = min(targets, key=lambda t: t[0])
                if target[0] <= weapon.range:
                    target[1].take_damage(weapon.power)
                    print(f"{target[1].name} a été frappé par {weapon.name}")

        elif weapon.weapon_type == "melee_aoe":
            for distance, pnj in targets:
                if distance <= weapon.range:
                    pnj.take_damage(weapon.power)
                    print(f"{pnj.name} a été frappé par {weapon.name} (AOE)")

        elif weapon.weapon_type == "ranged":
            for distance, pnj in targets:
                if distance == 0:
                    continue

                dx = pnj.position[0] - self.position[0]
                dz = pnj.position[2] - self.position[2]
                direction_to_enemy = (math.degrees(math.atan2(-dx, -dz))) % 360
                player_dir = self.rotation_y % 360
                angle_diff = abs((direction_to_enemy - player_dir + 180) % 360 - 180)
                print(f"[ANGLE DIFF OBSERVE] target = {pnj.name} angle diff = {angle_diff}")
                if angle_diff <= 15.0:
                    pnj.take_damage(weapon.power)
                    print(f"{pnj.name} a été frappé par {weapon.name} (ranged)")

    def take_damage(self, amount, renderer=None):
        if getattr(self, "_tmp_invincible_value", False):
            print("Dégâts ignorés (invincible)")
            return

        resistance = getattr(self, "_tmp_resist_value", 0)
        reduced = amount * (1 - resistance / 100)
        self.health = max(self.health - reduced, 0)
        print(f"Dégâts subis : {int(reduced)} (résistance {resistance}%) → Santé : {int(self.health)}")

        if renderer:
            renderer.damage_overlay_timer = 0.1

    def scroll_items(self, direction):
        if not self.inventory_items:
            self.item_index = 0
            return
        self.item_index = (self.item_index + direction) % len(self.inventory_items)

    def scroll_weapons(self, direction):
        if not self.inventory_weapons:
            self.weapon_index = 0
            return
        self.weapon_index = (self.weapon_index + direction) % len(self.inventory_weapons)
        self.equip(self.inventory_weapons[self.weapon_index])


    def get_selected_item(self):
        if 0 <= self.item_index < len(self.inventory_items):
            return self.inventory_items[self.item_index]
        return None

    def get_selected_weapon(self):
        if 0 <= self.weapon_index < len(self.inventory_weapons):
            return self.inventory_weapons[self.weapon_index]
        return None

    def use_selected_item(self):
        item = self.get_selected_item()
        if item:
            print(f"Utilisation de l’objet sélectionné : {item.id}")
            item.activate(self)
            if item.item_type != "weapon":
                self.inventory_items.remove(item)
                self.item_index = max(0, self.item_index - 1)

    def apply_effect(self, effect):
        etype = effect.get("type")
        value = effect.get("value", 0)
        duration = effect.get("duration", 0)

        if etype == "heal":
            self.health = min(self.health + value, 100)
            print(f"Santé +{value} → {self.health}")

        elif etype == "speed":
            self._apply_temporary_attr("speed", PLAYER_SPEED * (1 + value / 100), duration)

        elif etype == "resistance":
            self._apply_temporary_attr("resist", value, duration)

        elif etype == "invincible":
            self._apply_temporary_attr("invincible", True, duration)

    def _apply_temporary_attr(self, attr, value, duration):
        setattr(self, f"_tmp_{attr}_value", value)
        setattr(self, f"_tmp_{attr}_timer", duration)
        print(f"Effet temporaire : {attr} = {value} pendant {duration}s")
