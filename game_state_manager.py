# game_state_manager.py
import json
import os
from gameplay.game_session import GameSession

# Imports des états pour pouvoir relancer le jeu lors d'un chargement ou nouvelle partie
from states.interior_state import InteriorState
from states.overworld_state import OverworldState

class GameStateManager:
    """
    Gère la pile d'états de jeu et possède la Session de jeu active.
    C'est le chef d'orchestre de la persistance.
    """
    def __init__(self):
        self.states = []
        self.game_session = None # La session contenant les données persistantes (PV, Inventaire...)

    def push_state(self, state):
        self.states.append(state)

    def pop_state(self):
        if self.states:
            self.states.pop()

    def switch_state(self, state):
        while self.states:
            self.states.pop()
        self.states.append(state)

    def get_active_state(self):
        return self.states[-1] if self.states else None

    def update(self, delta_time):
        active_state = self.get_active_state()
        if active_state:
            active_state.update(delta_time)

    def render(self, screen):
        active_state = self.get_active_state()
        if active_state:
            active_state.render(screen)

    def start_new_session(self, screen):
        """
        Appelé par le Menu Principal pour lancer une nouvelle aventure.
        Crée une session vierge et lance la carte par défaut (Overworld).
        """
        print("Création d'une nouvelle session de jeu...")
        self.game_session = GameSession()
        
        # On récupère la carte par défaut définie dans la session
        initial_map = self.game_session.current_map
        
        # On lance l'état Overworld avec cette session
        # Note: On passe 'self' (le manager) qui contient maintenant la session
        first_state = OverworldState(self, screen, initial_map)
        self.switch_state(first_state)

    def save_game(self, slot_number=1):
        """
        Sauvegarde la session actuelle dans un fichier JSON.
        Synchronise d'abord les données du joueur actif vers la session.
        """
        if not self.game_session:
            print("Erreur: Aucune session active à sauvegarder.")
            return

        print(f"Préparation de la sauvegarde sur le slot {slot_number}...")

        # 1. SYNCHRONISATION : On cherche l'état de jeu actif pour récupérer les stats fraîches du joueur
        gameplay_state = None
        # On parcourt la pile à l'envers pour trouver le premier état de jeu (Interior ou Overworld)
        # Cela permet de sauvegarder même si on est dans l'état PauseState (qui est au dessus)
        for state in reversed(self.states):
            if isinstance(state, (InteriorState, OverworldState)):
                gameplay_state = state
                break
        
        if gameplay_state and hasattr(gameplay_state, 'player'):
            # On met à jour la session avec les PV, munitions et position actuels du joueur
            self.game_session.save_player_state(gameplay_state.player)
            print("Données du joueur synchronisées vers la session.")
        else:
            print("Attention : Pas d'état de jeu actif trouvé, sauvegarde de la session en l'état.")

        # 2. ÉCRITURE DISQUE
        save_data = self.game_session.to_dict()
        save_filename = f"savegame_{slot_number}.json"
        
        try:
            with open(save_filename, 'w') as f:
                json.dump(save_data, f, indent=4)
            print(f"Partie sauvegardée avec succès dans {save_filename}")
        except Exception as e:
            print(f"Erreur critique lors de la sauvegarde : {e}")

    def load_game(self, slot_number, screen):
        """
        Charge une session depuis un fichier JSON et relance le jeu au bon endroit.
        """
        save_filename = f"savegame_{slot_number}.json"
        if not os.path.exists(save_filename):
            print(f"Aucune sauvegarde trouvée à l'emplacement {slot_number}.")
            return False

        print(f"Chargement de la partie depuis {save_filename}...")
        try:
            with open(save_filename, 'r') as f:
                save_data = json.load(f)

            # 1. RECRÉATION DE LA SESSION
            self.game_session = GameSession()
            self.game_session.load_from_dict(save_data)

            # 2. DÉTERMINATION DE L'ÉTAT À LANCER
            current_map = self.game_session.current_map
            
            # Logique simple pour savoir si c'est un intérieur ou extérieur basé sur le nom du fichier
            # Convention: "ext_" = Overworld, "int_" = Interior
            filename = os.path.basename(current_map)
            
            if filename.startswith("int_"):
                print(f"Reprise en mode Intérieur sur {current_map}")
                # Note: Le spawn_id n'est pas sauvegardé précisément ici, on reprendra au spawn par défaut
                # ou il faudrait sauvegarder le last_spawn_id dans la session.
                new_state = InteriorState(self, screen, current_map)
            else:
                print(f"Reprise en mode Overworld sur {current_map}")
                new_state = OverworldState(self, screen, current_map)

            self.switch_state(new_state)
            print("Partie chargée avec succès !")
            return True

        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            import traceback
            traceback.print_exc()
            return False
