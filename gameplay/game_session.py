import json
from gameplay.serialization import serialize_object, deserialize_object

class GameSession:
    """
    Conteneur de données persistantes du joueur (Santé, Inventaire, Position Overworld).
    C'est cet objet qui est sauvegardé dans le fichier JSON.
    """
    def __init__(self):
        # Stats vitales
        self.player_stats = {
            "health": 100,
            "max_health": 100,
        }
        # Inventaire et équipement
        self.inventory_data = {
            "weapons": [], # Liste de dictionnaires sérialisés
            "items": [],   # Liste de dictionnaires sérialisés
            "ammo": { "9mm": 30, "shell": 10 },
            "current_weapon_index": 0
        }
        # État du monde
        self.flags = {} # Pour les quêtes plus tard
        self.current_map = "assets/maps/ext_overworld_test_map.json"
        self.overworld_position = None
        self.world_state = {}

    def save_player_state(self, player):
        """
        Extrait les données critiques de l'objet Player actif pour les stocker dans la session.
        À appeler AVANT de détruire un état de jeu (ex: quitter l'Overworld).
        """
        self.player_stats["health"] = player.health
        self.inventory_data["ammo"] = player.ammo_pool.copy()
        
        # On ignore les champs temporaires pour ne garder que la structure des objets
        ignore_list = ['attack_timer', 'state', 'visible']
        
        self.inventory_data["weapons"] = serialize_object(player.inventory_weapons, ignore_list)
        self.inventory_data["items"] = serialize_object(player.inventory_items, ignore_list)
        self.inventory_data["current_weapon_index"] = player.weapon_index

        # Si on est en mode 2D, on sauvegarde la position précise pour le retour
        if player.mode == "2D":
             self.overworld_position = [player.position[0], player.position[1]]

    def apply_to_player(self, player):
        """
        Injecte les données de la session dans un nouvel objet Player.
        """
        player.health = self.player_stats["health"]
        
        if self.inventory_data["ammo"]:
            player.ammo_pool = self.inventory_data["ammo"].copy()
        
        if self.inventory_data["weapons"]:
             player.inventory_weapons = deserialize_object(self.inventory_data["weapons"])
             
             for weapon in player.inventory_weapons:
                 if not hasattr(weapon, "state"): 
                     weapon.state = "idle"
                 if not hasattr(weapon, "attack_timer"): 
                     weapon.attack_timer = 0.0
     

             player.weapon_index = self.inventory_data["current_weapon_index"]
             
             if 0 <= player.weapon_index < len(player.inventory_weapons):
                 player.active_weapon = player.inventory_weapons[player.weapon_index]
             elif player.inventory_weapons:
                 player.weapon_index = 0
                 player.active_weapon = player.inventory_weapons[0]
        
        if self.inventory_data["items"]:
            player.inventory_items = deserialize_object(self.inventory_data["items"])

    def to_dict(self):
        return {
            "player_stats": self.player_stats,
            "inventory_data": self.inventory_data,
            "flags": self.flags,
            "current_map": self.current_map,
            "overworld_position": self.overworld_position,
            "world_state": self.world_state # Sauvegarde de l'état du monde
        }

    def load_from_dict(self, data):
        self.player_stats = data.get("player_stats", self.player_stats)
        self.inventory_data = data.get("inventory_data", self.inventory_data)
        self.flags = data.get("flags", self.flags)
        self.current_map = data.get("current_map", self.current_map)
        self.overworld_position = data.get("overworld_position", self.overworld_position)
        self.world_state = data.get("world_state", self.world_state) # Chargement
        
    def register_action(self, map_path, entity_type, entity_id):
        """Enregistre une action irréversible (collected, killed)."""
        if map_path not in self.world_state:
            self.world_state[map_path] = {"collected": [], "killed": []}
        
        target_list = self.world_state[map_path].get(entity_type)
        if target_list is not None and entity_id not in target_list:
            target_list.append(entity_id)

    def is_flagged(self, map_path, entity_type, entity_id):
        """Vérifie si une entité est marquée dans la session."""
        if map_path not in self.world_state:
            return False
        return entity_id in self.world_state[map_path].get(entity_type, [])
