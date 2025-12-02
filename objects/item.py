# objects/item.py

from objects.game_object import GameObject

class Item(GameObject):
    """
    Représente un objet interactif dans le monde du jeu, comme une potion, 
    une arme à ramasser ou un paquet de munitions.
    """
    
    def __init__(self, position=(0.0, 0.0, 0.0), item_type="potion", effect=None, weapon_attrs=None, ammo_attrs=None, obj_id=None):
        """
        Initialise un item.
        """
        super().__init__(position)
        self.item_type = item_type
        # Si un ID est fourni, on l'utilise. Sinon, ID temporaire.
        self.id = obj_id if obj_id else f"{item_type}_{id(self)}"
        
        self.collected = False
        
        # Stockage des attributs spécifiques au type
        self.effect = effect or {}
        self.weapon_attrs = weapon_attrs or {}
        self.ammo_attrs = ammo_attrs or {}

    def update(self, player, delta_time):
        """
        Vérifie si le joueur est assez proche pour ramasser l'objet.
        """
        if not self.collected and self._is_near(player.position):
            self.on_pickup(player)

    def draw(self, renderer):
        """
        Gère le rendu du sprite de l'item dans le monde.
        """
        if self.visible and not self.collected:
            sprite_name = f"sprites/{self.item_type}.png" 
            size = 0.25

            if self.item_type == "potion":
                sprite_name = f"sprites/potion_{self.effect.get('type', 'heal')}.png"
                size = 0.2
            elif self.item_type == "weapon":
                name = self.weapon_attrs.get("name", "unknown")
                sprite_name = f"sprites/weapon_{name}.png"
                size = 0.3

            renderer.draw_sprite(
                (self.position[0], 0.2, self.position[2]),
                texture_name=sprite_name,
                size=size
            )

    def on_pickup(self, player):
        """
        Gère ce qui se passe lorsque le joueur ramasse l'objet.
        """
        self.collected = True
        self.visible = False
        
        if self.item_type == "weapon":
            player.pickup_weapon(self)

        elif self.item_type == "ammo":
            ammo_type = self.ammo_attrs.get("type", "unknown")
            amount = self.ammo_attrs.get("amount", 0)
            player.add_ammo(ammo_type, amount)

        elif self.item_type == "key":
            print("Clé ramassée (logique à implémenter).")

        else: 
            player.add_to_inventory(self)

    def activate(self, player):
        """
        Active l'effet d'un item consommable (comme une potion) depuis l'inventaire.
        """
        if self.item_type == "potion":
            player.apply_effect(self.effect)

        if self in player.inventory_items:
            player.inventory_items.remove(self)
        player.item_index = max(0, player.item_index - 1)

    def _is_near(self, position, threshold=0.8):
        """Vérifie si une position est proche de l'item."""
        dx = self.position[0] - position[0]
        dz = self.position[2] - position[2]
        return (dx * dx + dz * dz) <= (threshold * threshold)
