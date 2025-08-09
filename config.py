# config.py

# --- AFFICHAGE ET FENÊTRE ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FOV = 75
NEAR_CLIP = 0.1
FAR_CLIP = 100.0
BACKGROUND_COLOR = (0.3, 0.3, 0.5, 1.0)
TARGET_FPS = 60

# --- JOUEUR ET MOUVEMENT ---
PLAYER_SPEED = 5.0
MOUSE_SENSITIVITY = 0.25

# --- CHEMINS ET FICHIERS ---
ASSETS_PATH = "assets/"
TEXTURES_PATH = ASSETS_PATH + "textures/"
SPRITES_PATH = ASSETS_PATH + "sprites/"
SOUNDS_PATH = ASSETS_PATH + "sounds/"
DEFAULT_MAP = "assets/maps/medium_map.json"

# --- NOUVEAU: CONFIGURATION DES ARMES ---
# Dictionnaire centralisant toutes les statistiques des armes.
# Cela permet d'équilibrer le jeu très facilement en modifiant simplement ces valeurs.
WEAPON_CONFIG = {


    "fist": {
        "weapon_type": "melee",
        "power": 15,
        "range": 0.8,
        "rpm": 120,
        "mag_size": 0,
        "ammo_type": "none",
        "melee_behavior": "single_target"  # <-- NOUVEL ATTRIBUT
    },
    "pistol": {
        # ... (pas de changement ici)
    },
    # EXEMPLE POUR LE FUTUR :
    # "sword": {
    #     "weapon_type": "melee",
    #     "power": 35,
    #     "range": 1.2,
    #     "rpm": 80,
    #     "ammo_type": "none",
    #     "melee_behavior": "area_effect" # <-- Pourrait toucher plusieurs cibles
    # }
# ...
    "pistol": {
        "weapon_type": "ranged",
        "power": 25,
        "range": 20.0,
        "rpm": 400,         # Cadence de tir semi-rapide
        "mag_size": 12,     # Taille du chargeur
        "ammo_type": "9mm"  # Type de munitions utilisées
    }
    # Vous pourrez ajouter d'autres armes ici plus tard, comme un fusil à pompe:
    # "shotgun": {
    #     "weapon_type": "ranged",
    #     "power": 80,
    #     "range": 10.0,
    #     "rpm": 60,
    #     "mag_size": 8,
    #     "ammo_type": "shell"
    # }
}
