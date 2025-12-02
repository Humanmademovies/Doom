# objects/item.py

from objects.game_object import GameObject
# La classe Weapon n'est plus directement nécessaire ici, car la création se fait dans Player
# from objects.weapon import Weapon 

class Item(GameObject):
    """
    Représente un objet interactif dans le monde du jeu, comme une potion, 
    une arme à ramasser ou un paquet de munitions.
    """
    
    def __init__(self, position=(0.0, 0.0, 0.0), item_type="potion", effect=None, weapon_attrs=None, ammo_attrs=None):
        """
        Initialise un item.

        Args:
            position (tuple): Position (x, y, z) de l'item dans le monde.
            item_type (str): Le type d'item ("potion", "weapon", "ammo", "key").
            effect (dict, optional): L'effet d'une potion (ex: {"type": "heal", "value": 25}).
            weapon_attrs (dict, optional): Les attributs d'une arme à ramasser (ex: {"name": "pistol"}).
            ammo_attrs (dict, optional): Les attributs d'un paquet de munitions (ex: {"type": "9mm", "amount": 20}).
        """
        super().__init__(position)
        self.item_type = item_type
        self.id = f"{item_type}_{id(self)}" # ID unique pour l'objet
        self.collected = False
        
        # Stockage des attributs spécifiques au type
        self.effect = effect or {}
        self.weapon_attrs = weapon_attrs or {}
        self.ammo_attrs = ammo_attrs or {}


    def update(self, player, delta_time):
        """
        Vérifie si le joueur est assez proche pour ramasser l'objet.
        """
        # Si l'objet n'a pas été collecté et que le joueur est proche...
        if not self.collected and self._is_near(player.position):
            # ...on appelle la logique de ramassage.
            self.on_pickup(player)

    def draw(self, renderer):
        """
        Gère le rendu du sprite de l'item dans le monde.
        """
        if self.visible and not self.collected:
            sprite_name = f"sprites/{self.item_type}.png" # Sprite par défaut
            size = 0.25

            # Logique pour choisir le bon sprite en fonction du type
            if self.item_type == "potion":
                sprite_name = f"sprites/potion_{self.effect.get('type', 'heal')}.png"
                size = 0.2
            elif self.item_type == "weapon":
                name = self.weapon_attrs.get("name", "unknown")
                sprite_name = f"sprites/weapon_{name}.png"
                size = 0.3
            # NOUVEAU: On pourrait ajouter un sprite spécifique pour les munitions plus tard
            # elif self.item_type == "ammo":
            #     sprite_name = f"sprites/ammo_{self.ammo_attrs.get('type')}.png"

            renderer.draw_sprite(
                (self.position[0], 0.2, self.position[2]),
                texture_name=sprite_name,
                size=size
            )


    def on_pickup(self, player):
        """
        MODIFIÉ: Gère ce qui se passe lorsque le joueur ramasse l'objet.
        La logique est maintenant aiguillée vers les méthodes spécifiques du joueur.
        """
        self.collected = True
        self.visible = False
        print(f"[PICKUP] Objet ramassé: {self.item_type}")

        # --- AIGUILLAGE SELON LE TYPE D'ITEM ---
        
        if self.item_type == "weapon":
            # On utilise la nouvelle méthode du joueur pour gérer le ramassage d'arme
            player.pickup_weapon(self)

        elif self.item_type == "ammo":
            # NOUVEAU: On utilise la méthode pour ajouter des munitions au pool du joueur
            ammo_type = self.ammo_attrs.get("type", "unknown")
            amount = self.ammo_attrs.get("amount", 0)
            player.add_ammo(ammo_type, amount)

        elif self.item_type == "key":
            # Les clés ou autres objets de quête peuvent être gérés ici
            print("Clé ramassée (logique à implémenter).")
            # player.add_key(self.id) par exemple

        else: # "potion" et autres consommables
            # Les objets consommables sont ajoutés à l'inventaire pour être utilisés plus tard
            player.add_to_inventory(self)

    def activate(self, player):
        """
        Active l'effet d'un item consommable (comme une potion) depuis l'inventaire.
        """
        if self.item_type == "potion":
            player.apply_effect(self.effect)

        # Une fois utilisé, l'objet est retiré de l'inventaire
        if self in player.inventory_items:
            player.inventory_items.remove(self)
        player.item_index = max(0, player.item_index - 1)

    def _is_near(self, position, threshold=0.8):
        """Vérifie si une position est proche de l'item."""
        dx = self.position[0] - position[0]
        dz = self.position[2] - position[2]
        return (dx * dx + dz * dz) <= (threshold * threshold)
