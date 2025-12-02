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
OVERWORLD_PLAYER_SPEED = 2.0
MOUSE_SENSITIVITY = 0.25

# --- CHEMINS ET FICHIERS ---
ASSETS_PATH = "assets/"
TEXTURES_PATH = ASSETS_PATH + "textures/"
SPRITES_PATH = ASSETS_PATH + "sprites/"
SOUNDS_PATH = ASSETS_PATH + "sounds/"
DEFAULT_MAP = "assets/maps/medium_map.json"

# --- CONFIGURATION DES SPRITES ET LOGOS ---
LOGO_SIZE = 64
LOGO_TARGET_SIZE = 128
PLAYER_HEIGHT_IN_TILES = 1
OVERWORLD_TILES_PER_SCREEN_HEIGHT = 8
PLAYER_SPRITE_SIZE = 64

# --- CONFIGURATION DES ARMES ---
WEAPON_CONFIG = {
    "fist": {
        "weapon_type": "melee",
        "power": 15,
        "range": 0.8,
        "rpm": 120,
        "mag_size": 0,
        "ammo_type": "none",
        "melee_behavior": "single_target"
    },
    "pistol": {
        "weapon_type": "ranged",
        "power": 25,
        "range": 20.0,
        "rpm": 400,
        "mag_size": 12,
        "ammo_type": "9mm"
    }
}
