# objects/item.py

from objects.game_object import GameObject
from objects.weapon import Weapon
class Item(GameObject):
    
    def __init__(self, position=(0.0, 0.0, 0.0), item_type="potion", item_id=None, effect=None, weapon_attrs=None):
        super().__init__(position)
        self.item_type = item_type
        self.id = item_id or f"{item_type}_{id(self)}"
        self.collected = False
        self.effect = effect or self._default_effect()
        self.weapon_attrs = weapon_attrs or {}


    def _default_effect(self):
        if self.item_type == "potion":
            return {"type": "heal", "value": 25}
        return {}



    def update(self, player):
        # Détection simple : proximité du joueur
        if not self.collected and self._is_near(player.position):
            self.on_pickup(player)

    def draw(self, renderer):
        if self.visible and not self.collected:

            if self.item_type == "potion" and hasattr(self, "effect"):
                effect_type = self.effect.get("type", "heal")
                sprite = f"potion_{effect_type}.png"
                size = 0.2
            elif self.item_type == "weapon" and hasattr(self, "weapon_attrs"):
                name = self.weapon_attrs.get("name", "unknown")
                sprite = f"weapon_{name}.png"
                size = 0.3
            else:
                sprite = f"{self.item_type}.png"
                size = 0.25

            # 🔍 Vérifie que le sprite est chargé
            if not renderer.textures.get(sprite):
                print(f"[SPRITE MANQUANT] {sprite} non trouvé dans renderer.textures")

            renderer.draw_sprite(
                (self.position[0], 0.2, self.position[2]),
                texture_name=sprite,
                size=size
            )


    def on_pickup(self, player):
        self.collected = True
        self.visible = False
        print(f"[PICKUP] {self.item_type} → {self.id}")

        if self.item_type == "weapon":
            # Ajout dans l'inventaire d'items pour affichage et gestion
            name = self.weapon_attrs.get("name", "custom")
            weapon = Weapon(
                name=name,
                weapon_type=self.weapon_attrs.get("weapon_type", "melee"),
                power=self.weapon_attrs.get("power", 10),
                range=self.weapon_attrs.get("range", 1.5)
            )
            weapon.ammo = self.weapon_attrs.get("ammo", 0)

            player.inventory_weapons.append(weapon)
            player.weapon_index = len(player.inventory_weapons) - 1
            player.equip(weapon)
            return  # éviter toute autre logique pour les armes

        elif self.item_type == "key":
            print("Clé ramassée (effet passif).")

        elif self.item_type == "ammo":
            for item in player.inventory:
                if hasattr(item, "item_type") and item.item_type == "weapon" and self.id.startswith(item.id):
                    item.ammo += 5  # valeur par défaut
                    print(f"Munition ajoutée à {item.id} → {item.ammo}")
                    return

        else:
            player.add_to_inventory(self)

        if self.item_type == "key":
            print("Clé ramassée (effet passif).")
            return

        elif self.item_type == "ammo":
            for item in player.inventory:
                if hasattr(item, "item_type") and item.item_type == "weapon" and self.id.startswith(item.id):
                    item.ammo += 5  # valeur par défaut
                    print(f"Munition ajoutée à {item.id} → {item.ammo}")
                    return

        else:
            player.add_to_inventory(self)


    def activate(self, player):
        if self.item_type == "potion":
            player.apply_effect(self.effect)

        elif self.item_type == "weapon":
            name = self.weapon_attrs.get("name", "custom")
            weapon = Weapon(
                name=name,
                weapon_type=self.weapon_attrs.get("weapon_type", "melee"),
                power=self.weapon_attrs.get("power", 10),
                range=self.weapon_attrs.get("range", 1.5)
            )
            weapon.ammo = self.weapon_attrs.get("ammo", 0)
            player.equip(weapon)

        # Ne pas garder l'item si ce n'est pas une arme
        if self.item_type != "weapon":
            if self in player.inventory_items:
                player.inventory_items.remove(self)
            player.item_index = max(0, player.item_index - 1)

    def _is_near(self, position, threshold=1.0):
        dx = self.position[0] - position[0]
        dz = self.position[2] - position[2]
        return dx * dx + dz * dz <= threshold * threshold

    def apply_effect(self, effect):
        etype = effect.get("type")
        value = effect.get("value", 0)
        duration = effect.get("duration", 0)

        if etype == "heal":
            self.health = min(self.health + value, 100)
            print(f"Santé +{value} → {self.health}")
        elif etype == "speed":
            self._apply_temporary_attr("speed", PLAYER_SPEED * (1 + value/100), duration)
        elif etype == "resistance":
            self._apply_temporary_attr("resist", value, duration)
        elif etype == "invincible":
            self._apply_temporary_attr("invincible", True, duration)

    def _apply_temporary_attr(self, attr, value, duration):
        setattr(self, f"_tmp_{attr}_value", value)
        setattr(self, f"_tmp_{attr}_timer", duration)
        print(f"Effet temporaire : {attr} = {value} pendant {duration}s")
