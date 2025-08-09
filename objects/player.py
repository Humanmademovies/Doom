# objects/player.py

import math
from objects.game_object import GameObject
from objects.weapon import Weapon
from config import PLAYER_SPEED, MOUSE_SENSITIVITY, WEAPON_CONFIG

class Player(GameObject):
    def __init__(self, position=(1.0, 0.0, 1.0)):
        super().__init__(position)
        self.health = 100
        self.level = 1
        self.rotation_y = 0.0

        # --- GESTION DE L'INVENTAIRE ET DES ARMES ---
        self.inventory_items = []
        self.inventory_weapons = []
        self.item_index = 0
        self.weapon_index = 0
        
        # Le joueur commence avec une arme par défaut, les "poings".
        # On utilise la configuration de WEAPON_CONFIG pour l'initialiser.
        fist_config = WEAPON_CONFIG.get("fist", {})
        self.active_weapon = Weapon(name="fist", **fist_config)

        # NOUVEAU: Le pool de munitions centralisé.
        # C'est un dictionnaire qui stocke la quantité de chaque type de munition.
        # Exemple: {"9mm": 100, "shell": 20}
        self.ammo_pool = {
            "9mm": 30,
            "shell": 10
        }

        # NOUVEAU: Le timer d'attaque et le statut `can_attack` sont maintenant
        # gérés directement dans la classe Weapon. Nous les supprimons d'ici.
        # self.attack_timer = 0.0 --> Supprimé
        # self.can_attack = True --> Supprimé

    def _is_in_view(self, target, fov=60.0):
        # ... (Aucun changement dans cette méthode)
        dx = target.position[0] - self.position[0]
        dz = target.position[2] - self.position[2]
        angle_to_target = (math.degrees(math.atan2(-dx, -dz))) % 360
        player_angle = self.rotation_y % 360
        diff = (angle_to_target - player_angle + 180) % 360 - 180
        in_view = abs(diff) <= (fov / 2)
        return in_view

    def _has_line_of_sight(self, target, game_map):
        # ... (Aucun changement dans cette méthode)
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
        # Mise à jour du mouvement et de la rotation (logique existante)
        # ...
        rad = math.radians(-self.rotation_y)
        sin_y, cos_y = math.sin(rad), math.cos(rad)
        self.rotation_y -= mouse_delta[0] * MOUSE_SENSITIVITY
        self.rotation_y %= 360
        speed_boost = getattr(self, "_tmp_speed_value", PLAYER_SPEED)
        
        dx = (movement_vector[1] * cos_y + movement_vector[0] * sin_y) * speed_boost * delta_time
        dz = (movement_vector[1] * sin_y - movement_vector[0] * cos_y) * speed_boost * delta_time

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
        
        # NOUVEAU: Mettre à jour l'arme active (pour son timer interne)
        self.active_weapon.update(delta_time)

        # Si l'animation d'attaque est terminée, on repasse en idle.
        if self.active_weapon.state == "attack" and self.active_weapon.can_attack():
            self.active_weapon.set_state("idle")

        # Gestion des effets temporaires (potions, etc.)
        for attr in ["speed", "resist", "invincible"]:
            timer = getattr(self, f"_tmp_{attr}_timer", 0)
            if timer > 0:
                timer -= delta_time
                setattr(self, f"_tmp_{attr}_timer", timer)
                if timer <= 0:
                    setattr(self, f"_tmp_{attr}_value", None)
                    print(f"Effet temporaire terminé : {attr}")

def fire(self, pnjs, game_map): # MODIFIÉ: Ajout des paramètres
        """
        Gère la logique de tir. C'est cette méthode qui sera appelée 
        dans la boucle de jeu principale.
        """
        if self.health <= 0:
            return

        shot_fired = self.active_weapon.perform_attack()

        if shot_fired:
            targets = []
            # On utilise maintenant les pnjs et la game_map passés en argument
            for pnj in pnjs:
                if hasattr(pnj, "health") and pnj.health > 0:
                    if self._is_in_view(pnj) and self._has_line_of_sight(pnj, game_map):
                        dx = pnj.position[0] - self.position[0]
                        dz = pnj.position[2] - self.position[2]
                        distance = (dx**2 + dz**2) ** 0.5
                        targets.append((distance, pnj))
            
            self._apply_damage_to_targets(targets)

    def _apply_damage_to_targets(self, targets):
        """Ajusté pour ne plus prendre d'arguments inutiles."""
        weapon = self.active_weapon
        
        if weapon.weapon_type == "melee":
            if targets:
                target = min(targets, key=lambda t: t[0])
                if target[0] <= weapon.range:
                    target[1].take_damage(weapon.power)
                    print(f"{target[1].name} a été frappé par {weapon.name}")

        elif weapon.weapon_type == "ranged":
            # Pour un tir à distance, on touche la première cible dans la ligne de mire
            if targets:
                target = min(targets, key=lambda t: t[0])
                if target[0] <= weapon.range:
                    target[1].take_damage(weapon.power)
                    print(f"{target[1].name} a été touché par {weapon.name} (ranged)")
                    
    def reload_weapon(self):
        """
        NOUVELLE MÉTHODE: Gère le rechargement de l'arme.
        """
        if self.active_weapon:
            print(f"Tentative de rechargement pour {self.active_weapon.name}...")
            # On appelle la méthode de rechargement de l'arme,
            # en lui passant notre pool de munitions.
            ammo_used = self.active_weapon.reload(self.ammo_pool)
            
            # Si des munitions ont été utilisées, on les retire du pool.
            if ammo_used > 0:
                self.ammo_pool[self.active_weapon.ammo_type] -= ammo_used
                print(f"Pool de '{self.active_weapon.ammo_type}' restant : {self.ammo_pool[self.active_weapon.ammo_type]}")

    def equip(self, weapon):
        """Équipe une arme et met à jour l'arme active."""
        self.active_weapon = weapon
        self.active_weapon.set_state("idle")

    def scroll_weapons(self, direction):
        """Fait défiler l'inventaire des armes."""
        if not self.inventory_weapons:
            return
        
        self.weapon_index = (self.weapon_index + direction) % len(self.inventory_weapons)
        self.equip(self.inventory_weapons[self.weapon_index])

    def take_damage(self, amount, renderer=None):
        # ... (Aucun changement dans cette méthode)
        if getattr(self, "_tmp_invincible_value", False):
            print("Dégâts ignorés (invincible)")
            return
        resistance = getattr(self, "_tmp_resist_value", 0)
        reduced = amount * (1 - resistance / 100)
        self.health = max(self.health - reduced, 0)
        print(f"Dégâts subis : {int(reduced)} (résistance {resistance}%) → Santé : {int(self.health)}")
        if renderer:
            renderer.damage_overlay_timer = 0.1

    # --- MÉTHODES DE GESTION D'INVENTAIRE (ITEMS) ---
    def add_to_inventory(self, item):
        # La logique de gestion d'armes est maintenant dans 'pickup_weapon'
        if item.item_type != "weapon":
            self.inventory_items.append(item)
            self.item_index = len(self.inventory_items) - 1

    def pickup_weapon(self, item):
        """
        NOUVELLE MÉTHODE: Spécifiquement pour ramasser une arme.
        """
        # Créer une nouvelle instance d'arme à partir de l'item ramassé
        weapon_config = WEAPON_CONFIG.get(item.weapon_attrs.get("name"), {})
        new_weapon = Weapon(**weapon_config)

        # Ajouter l'arme à l'inventaire et l'équiper
        self.inventory_weapons.append(new_weapon)
        self.weapon_index = len(self.inventory_weapons) - 1
        self.equip(new_weapon)
        print(f"Arme ramassée et équipée : {new_weapon.name}")

    def add_ammo(self, ammo_type, amount):
        """
        NOUVELLE MÉTHODE: Pour ajouter des munitions au pool.
        """
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
            print(f"Utilisation de l’objet : {item.id}")
            item.activate(self)
    
    def apply_effect(self, effect):
        # ... (Aucun changement dans cette méthode)
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
