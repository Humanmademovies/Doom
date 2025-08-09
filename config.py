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
        "range": 1.5,
        "rpm": 120,         # Cadence de frappe (plus basse que les armes à feu)
        "mag_size": 0,      # Pas de chargeur
        "ammo_type": "none" # Pas de munitions
    },
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
