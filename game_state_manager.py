# game_state_manager.py
import json
import os
from gameplay.serialization import serialize_object, deserialize_object

# On a besoin de connaître les classes pour la désérialisation, mais on veut éviter les imports circulaires.
# C'est une astuce pour que le code fonctionne sans erreur.
from states.interior_state import InteriorState

class GameStateManager:
    """
    Gère une pile d'états de jeu (ex: menu, jeu, pause).
    Seul l'état au sommet de la pile est actif.
    """
    def __init__(self):
        self.states = []

    def push_state(self, state):
        """Ajoute un état au sommet de la pile."""
        self.states.append(state)

    def pop_state(self):
        """Retire l'état au sommet de la pile."""
        if self.states:
            self.states.pop()

    def switch_state(self, state):
        """Remplace tous les états actuels par un nouveau."""
        while self.states:
            self.states.pop()
        self.states.append(state)

    def get_active_state(self):
        """Retourne l'état actif, s'il y en a un."""
        return self.states[-1] if self.states else None

    def update(self, delta_time):
        """Met à jour l'état actif."""
        active_state = self.get_active_state()
        if active_state:
            active_state.update(delta_time)

    def render(self, screen):
        """Gère le rendu de l'état actif."""
        active_state = self.get_active_state()
        if active_state:
            active_state.render(screen)

    def save_game(self, slot_number=1):
        """
        CORRIGÉ: Sauvegarde l'état du jeu, même depuis le menu pause.
        """
        print(f"Tentative de sauvegarde sur l'emplacement {slot_number}...")
        
        # On cherche l'état du jeu dans la pile, quel que soit l'état actif
        game_state = None
        for state in self.states:
            if isinstance(state, InteriorState):
                game_state = state
                break

        if game_state:
            game_engine = game_state.game_engine
            
            # --- CORRECTION ---
            # On retire 'patrol_points' de la liste des attributs à ignorer.
            ignore = ['screen', 'renderer', 'input_manager', 'font', 'damage_overlay_timer', 'camera_position', 'textures']

            save_data = {
                "player": serialize_object(game_engine.player, ignore),
                "pnjs": serialize_object(game_engine.pnjs, ignore),
                "items": serialize_object(game_engine.items, ignore),
                "map_name": game_engine.game_map.current_map_path
            }
            
            save_filename = f"savegame_{slot_number}.json"
            with open(save_filename, 'w') as f:
                json.dump(save_data, f, indent=4, default=lambda o: '<not serializable>')
            
            print(f"Partie sauvegardée avec succès dans {save_filename}")
        else:
            print("Sauvegarde impossible : aucun état de jeu trouvé dans la pile.")

    def load_game(self, slot_number=1):
        """
        CORRIGÉ: Charge une partie, même depuis le menu pause.
        """
        save_filename = f"savegame_{slot_number}.json"
        if not os.path.exists(save_filename):
            print(f"Aucune sauvegarde trouvée à l'emplacement {slot_number}.")
            return

        print(f"Chargement de la partie depuis {save_filename}...")
        with open(save_filename, 'r') as f:
            save_data = json.load(f)

        # On cherche l'état de jeu à mettre à jour
        game_state = None
        for state in self.states:
            if isinstance(state, InteriorState):
                game_state = state
                break

        if game_state:
            game_engine = game_state.game_engine

            # Recharger la bonne carte
            game_engine.game_map.load_from_file(save_data["map_name"])
            
            # Recréer les objets depuis les données sauvegardées
            game_engine.player = deserialize_object(save_data["player"])
            game_engine.pnjs = deserialize_object(save_data["pnjs"])
            game_engine.items = deserialize_object(save_data["items"])
            
            # Important : s'assurer que les objets non sauvegardés sont ré-initialisés
            game_engine.renderer.load_textures()
            
            print("Partie chargée avec succès !")
        else:
            print("Chargement impossible : il faut être en jeu.")
