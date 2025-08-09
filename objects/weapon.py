# objects/weapon.py

class Weapon:
    """
    Représente une arme avec des caractéristiques de tir, de munitions et d'état.
    Cette classe est conçue pour être flexible et gérer différents types d'armes
    (mêlée, à distance, etc.) avec des modes de tir variés.
    """
    def __init__(self, name="fist", weapon_type="melee", power=10, range=1.5, rpm=300, mag_size=10, ammo_type="none"):
        """
        Initialise une nouvelle arme.

        Args:
            name (str): Le nom de l'arme (ex: "pistol"). Utilisé pour les chemins de sprites.
            weapon_type (str): Le type de l'arme ("melee", "ranged").
            power (int): Les dégâts infligés par un tir réussi.
            range (float): La portée maximale de l'arme.
            rpm (int): "Rounds Per Minute", la cadence de tir.
            mag_size (int): La taille du chargeur.
            ammo_type (str): Le type de munitions utilisé (ex: "9mm", "shell"). "none" pour les armes sans munitions.
        """
        self.name = name
        self.weapon_type = weapon_type
        self.power = power
        self.range = range

        # --- NOUVEAUX ATTRIBUTS POUR LA GESTION DU TIR ---

        # Cadence de tir : convertit les "tours par minute" en secondes par tir.
        # Par exemple, 600 RPM = 10 tirs/seconde = 0.1s entre chaque tir.
        self.fire_rate = 60.0 / rpm if rpm > 0 else 0.5

        # Minuterie pour gérer la cadence de tir.
        self.attack_timer = 0.0

        # État actuel de l'arme pour l'animation (ex: "idle", "attack").
        self.state = "idle"

        # --- NOUVEAUX ATTRIBUTS POUR LA GESTION DES MUNITIONS ---

        self.mag_size = mag_size            # Taille maximale du chargeur
        self.ammo_type = ammo_type          # Type de munitions (pour le partage entre armes)
        self.ammo_loaded = mag_size         # Munitions actuellement dans l'arme

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
