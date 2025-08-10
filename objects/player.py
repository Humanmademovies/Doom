# objects/player.py

import math
import pygame
from objects.game_object import GameObject
from objects.weapon import Weapon
from config import PLAYER_SPEED, MOUSE_SENSITIVITY, WEAPON_CONFIG, OVERWORLD_PLAYER_SPEED

class Player(GameObject):
    def __init__(self, position=(1.0, 0.0, 1.0)):
        super().__init__(position)
        self.health = 100
        self.level = 1
        self.rotation_y = 0.0
        self.mode = "3D"
        self.size_2d = 64

        self.inventory_items = []
        self.item_index = 0
        
        fist_config = WEAPON_CONFIG.get("fist", {})
        fist_weapon = Weapon(name="fist", **fist_config)
        
        self.inventory_weapons = [fist_weapon]
        self.weapon_index = 0
        self.active_weapon = self.inventory_weapons[self.weapon_index]

        self.ammo_pool = {
            "9mm": 30,
            "shell": 10
        }

    def _is_in_view(self, target, fov=60.0):
        dx = target.position[0] - self.position[0]
        dz = target.position[2] - self.position[2]
        angle_to_target = (math.degrees(math.atan2(-dx, -dz))) % 360
        player_angle = self.rotation_y % 360
        diff = (angle_to_target - player_angle + 180) % 360 - 180
        in_view = abs(diff) <= (fov / 2)
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

    def update(self, movement_vector, mouse_delta, delta_time, game_map, tile_size=None):
        """
        Gère la mise à jour du joueur pour les modes 2D et 3D.
        'tile_size' est optionnel pour la compatibilité avec le mode 3D.
        """
        if self.mode == "3D":
            self._update_3d_movement(movement_vector, mouse_delta, delta_time, game_map)
        elif self.mode == "2D":
            if tile_size is None:
                raise ValueError("tile_size must be provided for 2D mode")
            self._update_2d_movement(movement_vector, delta_time, game_map, tile_size)

        self.active_weapon.update(delta_time)
        if self.active_weapon.state == "attack" and self.active_weapon.can_attack():
            self.active_weapon.set_state("idle")

        for attr in ["speed", "resist", "invincible"]:
            timer = getattr(self, f"_tmp_{attr}_timer", 0)
            if timer > 0:
                timer -= delta_time
                setattr(self, f"_tmp_{attr}_timer", timer)
                if timer <= 0:
                    setattr(self, f"_tmp_{attr}_value", None)
                    print(f"Effet temporaire terminé : {attr}")

    def _update_3d_movement(self, movement_vector, mouse_delta, delta_time, game_map):
        forward, strafe = movement_vector
        rad = math.radians(-self.rotation_y)
        sin_y, cos_y = math.sin(rad), math.cos(rad)

        self.rotation_y -= mouse_delta[0] * MOUSE_SENSITIVITY
        self.rotation_y %= 360

        speed = getattr(self, "_tmp_speed_value", PLAYER_SPEED)
        
        dx = (forward * cos_y + strafe * sin_y) * speed * delta_time
        dz = (forward * sin_y - strafe * cos_y) * speed * delta_time

        offset = 0.2
        
        next_x = self.position[0] + dx
        cell_x = int(next_x + (offset if dx > 0 else -offset))
        cell_z = int(-self.position[2])
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]) and game_map.grid[cell_z][cell_x] in game_map.floor_textures:
            self.position[0] = next_x

        next_z = self.position[2] + dz
        cell_x = int(self.position[0])
        cell_z = int(-next_z + (offset if dz < 0 else -offset))
        if 0 <= cell_z < len(game_map.grid) and 0 <= cell_x < len(game_map.grid[0]) and game_map.grid[cell_z][cell_x] in game_map.floor_textures:
            self.position[2] = next_z

    def _update_2d_movement(self, movement_vector, delta_time, game_map, tile_size):
        """
        MODIFIÉ: Utilise un masque de collision qui représente uniquement le rectangle du bâtiment,
        permettant au joueur d'accéder aux portes qui sont géométriquement à l'extérieur.
        """
        strafe, forward = movement_vector
        speed_in_pixels = getattr(self, "_tmp_speed_value", OVERWORLD_PLAYER_SPEED) * tile_size
        
        dx = strafe * speed_in_pixels * delta_time
        dy = forward * speed_in_pixels * delta_time * -1
        
        current_pixel_x = self.position[0] * tile_size
        current_pixel_y = self.position[1] * tile_size

        player_mask = pygame.mask.Mask((int(self.size_2d), int(self.size_2d)), True)

        # Mouvement en X
        next_pixel_x = current_pixel_x + dx
        collision_x = False
        for building in game_map.building_positions:
            if not building.get('mask'): continue
            
            scale_ratio = (tile_size * 0.5) / 64 # LOGO_SIZE
            
            scaled_width = int(building['texture_width'] * scale_ratio)
            scaled_height = int(building['texture_height'] * scale_ratio)
            if scaled_width == 0 or scaled_height == 0: continue
            
            scaled_building_mask = building['mask'].scale((scaled_width, scaled_height))
            
            scaled_anchor_x = building['anchor_x'] * scale_ratio
            scaled_anchor_y = building['anchor_y'] * scale_ratio
            
            # Position du coin de l'image entière du bâtiment
            building_image_x = building['x'] * tile_size - scaled_anchor_x
            building_image_y = building['y'] * tile_size - scaled_anchor_y
            
            # L'offset est maintenant entre le joueur et le coin de l'image
            offset_x = (next_pixel_x - self.size_2d / 2) - building_image_x
            offset_y = (current_pixel_y - self.size_2d / 2) - building_image_y

            if scaled_building_mask.overlap(player_mask, (int(offset_x), int(offset_y))):
                collision_x = True
                break
        
        if not collision_x:
            current_pixel_x = next_pixel_x

        # Mouvement en Y
        next_pixel_y = current_pixel_y + dy
        collision_y = False
        for building in game_map.building_positions:
            if not building.get('mask'): continue

            scale_ratio = (tile_size * 0.5) / 64
            scaled_width = int(building['texture_width'] * scale_ratio)
            scaled_height = int(building['texture_height'] * scale_ratio)
            if scaled_width == 0 or scaled_height == 0: continue
            
            scaled_building_mask = building['mask'].scale((scaled_width, scaled_height))

            scaled_anchor_x = building['anchor_x'] * scale_ratio
            scaled_anchor_y = building['anchor_y'] * scale_ratio
            
            building_image_x = building['x'] * tile_size - scaled_anchor_x
            building_image_y = building['y'] * tile_size - scaled_anchor_y
            
            offset_x = (current_pixel_x - self.size_2d / 2) - building_image_x
            offset_y = (next_pixel_y - self.size_2d / 2) - building_image_y

            if scaled_building_mask.overlap(player_mask, (int(offset_x), int(offset_y))):
                collision_y = True
                break
        
        if not collision_y:
            current_pixel_y = next_pixel_y

        self.position[0] = current_pixel_x / tile_size
        self.position[1] = current_pixel_y / tile_size


    def draw(self, renderer):
        pass

    def fire(self, pnjs, game_map):
        if self.health <= 0:
            return

        shot_fired = self.active_weapon.perform_attack()

        if shot_fired:
            targets = []
            for pnj in pnjs:
                if hasattr(pnj, "health") and pnj.health > 0:
                    if self._is_in_view(pnj) and self._has_line_of_sight(pnj, game_map):
                        dx = pnj.position[0] - self.position[0]
                        dz = pnj.position[2] - self.position[2]
                        distance = (dx**2 + dz**2) ** 0.5
                        targets.append((distance, pnj))
            
            self._apply_damage_to_targets(targets)

    def _apply_damage_to_targets(self, targets):
        weapon = self.active_weapon

        if not targets:
            return

        if weapon.weapon_type == "ranged":
            closest_target = min(targets, key=lambda t: t[0])
            distance_to_target, pnj_to_damage = closest_target
            if distance_to_target <= weapon.range:
                pnj_to_damage.take_damage(weapon.power)

        elif weapon.weapon_type == "melee":
            
            if weapon.melee_behavior == "single_target":
                closest_target = min(targets, key=lambda t: t[0])
                distance_to_target, pnj_to_damage = closest_target
                if distance_to_target <= weapon.range:
                    print(f"Coup de poing touche {pnj_to_damage.name}!")
                    pnj_to_damage.take_damage(weapon.power)
                else:
                    print("Coup de poing dans le vide.")

            elif weapon.melee_behavior == "area_effect":
                enemies_hit = 0
                for distance, pnj in targets:
                    if distance <= weapon.range:
                        print(f"Balayage touche {pnj.name}!")
                        pnj.take_damage(weapon.power)
                        enemies_hit += 1
                if enemies_hit == 0:
                    print("Balayage dans le vide.")
                    
    def reload_weapon(self):
        if self.active_weapon:
            ammo_used = self.active_weapon.reload(self.ammo_pool)
            if ammo_used > 0:
                self.ammo_pool[self.active_weapon.ammo_type] -= ammo_used

    def equip(self, weapon):
        self.active_weapon = weapon
        self.active_weapon.set_state("idle")

    def scroll_weapons(self, direction):
        if not self.inventory_weapons:
            return
        
        self.weapon_index = (self.weapon_index + direction) % len(self.inventory_weapons)
        self.equip(self.inventory_weapons[self.weapon_index])

    def take_damage(self, amount, renderer=None):
        if getattr(self, "_tmp_invincible_value", False):
            return
        resistance = getattr(self, "_tmp_resist_value", 0)
        reduced = amount * (1 - resistance / 100)
        self.health = max(self.health - reduced, 0)
        if renderer:
            renderer.damage_overlay_timer = 0.1

    def add_to_inventory(self, item):
        if item.item_type != "weapon":
            self.inventory_items.append(item)
            self.item_index = len(self.inventory_items) - 1

    def pickup_weapon(self, item):
        weapon_name = item.weapon_attrs.get("name")
        if not weapon_name:
            return

        weapon_config = WEAPON_CONFIG.get(weapon_name, {})
        new_weapon = Weapon(name=weapon_name, **weapon_config)
        self.inventory_weapons.append(new_weapon)
        self.weapon_index = len(self.inventory_weapons) - 1
        self.equip(new_weapon)

    def add_ammo(self, ammo_type, amount):
        if ammo_type in self.ammo_pool:
            self.ammo_pool[ammo_type] += amount
        else:
            self.ammo_pool[ammo_type] = amount
        print(f"Ramassé {amount} munitions de type '{ammo_type}'. Total : {self.ammo_pool[ammo_type]}")

    def scroll_items(self, direction):
        if not self.inventory_items: return
        self.item_index = (self.item_index + direction) % len(self.inventory_items)

    def get_selected_item(self):
        if 0 <= self.item_index < len(self.inventory_items):
            return self.inventory_items[self.item_index]
        return None
        
    def use_selected_item(self):
        item = self.get_selected_item()
        if item:
            item.activate(self)
    
    def apply_effect(self, effect):
        etype = effect.get("type")
        value = effect.get("value", 0)
        duration = effect.get("duration", 0)
        if etype == "heal":
            self.health = min(self.health + value, 100)
        elif etype == "speed":
            self._apply_temporary_attr("speed", PLAYER_SPEED * (1 + value / 100), duration)
        elif etype == "resistance":
            self._apply_temporary_attr("resist", value, duration)
        elif etype == "invincible":
            self._apply_temporary_attr("invincible", True, duration)

    def _apply_temporary_attr(self, attr, value, duration):
        setattr(self, f"_tmp_{attr}_value", value)
        setattr(self, f"_tmp_{attr}_timer", duration)
