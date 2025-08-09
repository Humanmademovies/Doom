# objects/weapon.py

class Weapon:
    """
    Représente une arme avec des caractéristiques de tir, de munitions et d'état.
    Cette classe est conçue pour être flexible et gérer différents types d'armes
    (mêlée, à distance, etc.) avec des modes de tir variés.
    """
    def __init__(self, name="fist", weapon_type="melee", power=10, range=1.5, rpm=300, mag_size=10, ammo_type="none", melee_behavior="single_target"):
        """
        Initialise une nouvelle arme.
        ...
        Args:
            # ... (autres arguments)
            melee_behavior (str): Comportement pour les armes de mêlée ('single_target' ou 'area_effect').
        """
        self.name = name
        self.weapon_type = weapon_type
        self.power = power
        self.range = range
        self.fire_rate = 60.0 / rpm if rpm > 0 else 0.5
        self.attack_timer = 0.0
        self.state = "idle"
        self.mag_size = mag_size
        self.ammo_loaded = mag_size
        self.ammo_type = ammo_type
        self.melee_behavior = melee_behavior # <-- On stocke le nouvel attribut

    def set_state(self, new_state):
        """
        Met à jour l'état de l'arme pour contrôler l'animation affichée sur le HUD.
        S'assure que les états valides sont utilisés.
        """
        if new_state in ("idle", "walk", "attack", "reload"):
            self.state = new_state
            #print(f"DEBUG: Weapon '{self.name}' state set to '{self.state}'") # Ligne de debug, peut être retirée
        
    def update(self, delta_time):
        """
        Met à jour la minuterie de l'arme. Appelé à chaque frame.
        """
        if self.attack_timer > 0:
            self.attack_timer -= delta_time

    def can_attack(self):
        """
        Vérifie si l'arme est prête à tirer (si le temps de recharge est écoulé).
        """
        return self.attack_timer <= 0

    def perform_attack(self):
        """
        Déclenche une attaque et réinitialise la minuterie de cadence de tir.
        """
        if self.can_attack():
            if self.ammo_type != "none":
                if self.ammo_loaded > 0:
                    self.ammo_loaded -= 1
                    self.attack_timer = self.fire_rate
                    self.set_state("attack")
                    return True # Le tir a réussi
                else:
                    # Gérer le "clic" à vide plus tard (son, etc.)
                    print(f"Chargeur de '{self.name}' vide !")
                    return False # Le tir a échoué
            else: # Arme de mêlée ou sans munitions
                self.attack_timer = self.fire_rate
                self.set_state("attack")
                return True
        return False

    def reload(self, ammo_pool):
        """
        Recharge l'arme en utilisant les munitions du pool du joueur.

        Args:
            ammo_pool (dict): Le dictionnaire de munitions du joueur (ex: {"9mm": 50}).

        Returns:
            int: Le nombre de munitions utilisées pour le rechargement.
        """
        if self.ammo_type == "none" or self.ammo_loaded == self.mag_size:
            return 0 # Ne peut pas recharger

        # Récupère les munitions disponibles pour ce type d'arme
        ammo_available = ammo_pool.get(self.ammo_type, 0)
        
        # Calcule le nombre de munitions nécessaires
        needed = self.mag_size - self.ammo_loaded

        if ammo_available > 0 and needed > 0:
            # Transfère le minimum entre ce qui est nécessaire et ce qui est disponible
            transfer = min(needed, ammo_available)
            self.ammo_loaded += transfer
            print(f"Rechargé '{self.name}' avec {transfer} munitions de type '{self.ammo_type}'.")
            return transfer # Retourne combien de munitions ont été retirées du pool
            
        print(f"Pas assez de munitions ('{self.ammo_type}') pour recharger.")
        return 0
