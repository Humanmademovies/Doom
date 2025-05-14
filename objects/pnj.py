import json
import os
from objects.game_object import GameObject

class PNJ(GameObject):
    def __init__(self, name, position=(0, 0, 0), action="idle"):
        super().__init__(position)
        self.name = name
        self.dmg_timer = 0.0

        config_path = os.path.join("assets", "pnj", name, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration introuvable pour le PNJ '{name}'")

        with open(config_path, "r") as f:
            data = json.load(f)

        self.P = data.get("P", 5)
        self.S = data.get("S", 5)
        self.I = data.get("I", 5)
        self.health = data.get("PV", 100)
        self.size = data.get("size", 1.0)
        self.mode = data.get("mode", "neutral")
        self.inventory_index = 0
        self.state = action
        self.sprite = f"{self.name}_{action}.png"
        self.visible = True
        self.position = (position[0], self.size , position[2])
        self.speed = 1.0

    def set_action(self, action):
        if self.dmg_timer > 0 and action != "dmg":
            return  # ne pas écraser un sprite de blessure encore actif
        if self.state == "dead" and action != "dead":
            return  # ne pas écraser un sprite de mort
        self.state = action
        self.sprite = f"{self.name}_{action}.png"


    def update(self, player, delta_time, game_map, renderer):

        if self.dmg_timer > 0:
            self.dmg_timer -= delta_time
            if self.dmg_timer <= 0 and self.health > 0:
                self.set_action("idle")  # ou autre action par défaut


    def draw(self, renderer):
        if self.visible:
            pos = list(self.position)
            if self.state == "dead":
                pos[1] = 0.2  # poser le sprite au sol
                self.size = 0.2
            if self.sprite == "monster_dmg.png":
                print(f"[DRAW] {self.name} utilise le sprite {self.sprite}")
            renderer.draw_sprite(tuple(pos), self.sprite, self.size)



    def take_damage(self, amount):
        self.health -= amount
        print(f"{self.name} a subi {amount} points de dégâts. PV restants : {self.health}")

        if self.health <= 0:
            self.health = 0
            self.set_action("dead")
            self.sprite = f"{self.name}_dead.png"
            print(f"{self.name} est mort.")
        else:
            self.sprite = f"{self.name}_dmg.png"
            self.dmg_timer = 0.2  # durée d'affichage du sprite de blessure

    def scroll_inventory(self, direction):
        if not self.inventory:
            self.inventory_index = 0
            return

        self.inventory_index = (self.inventory_index + direction) % len(self.inventory)

    def get_selected_item(self):
        if 0 <= self.inventory_index < len(self.inventory):
            return self.inventory[self.inventory_index]
        return None
