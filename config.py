# config.py

# Dimensions de la fenêtre
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Paramètres de rendu et de caméra
FOV = 75  # Champ de vision en degrés
RENDER_DISTANCE = 20.0  # Distance maximale de rendu
NEAR_CLIP = 0.1  # Plan de clipping proche
FAR_CLIP = 100.0  # Plan de clipping éloigné

# Paramètres de jeu
PLAYER_SPEED = 5.0  # Unités par seconde
MOUSE_SENSITIVITY = 0.25  # Sensibilité à la souris

# Framerate
TARGET_FPS = 60

# Chemins des ressources
ASSETS_PATH = "assets/"
TEXTURES_PATH = ASSETS_PATH + "textures/"
SPRITES_PATH = ASSETS_PATH + "sprites/"
SOUNDS_PATH = ASSETS_PATH + "sounds/"

# Couleurs de fond (RGBA)
BACKGROUND_COLOR = (0.3, 0.3, 0.5, 1.0)


# Options diverses
DEBUG_MODE = False  # Activer les logs ou rendus supplémentaires pour le développement
FULLSCREEN = False  # Mode plein écran (à intégrer dans les options utilisateur)

# Configuration modifiable (optionnel)
import json
import os

CONFIG_FILE = "settings.json"

def load_config():
    global SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                SCREEN_WIDTH = data.get("screen_width", SCREEN_WIDTH)
                SCREEN_HEIGHT = data.get("screen_height", SCREEN_HEIGHT)
                FULLSCREEN = data.get("fullscreen", FULLSCREEN)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")

def save_config():
    data = {
        "screen_width": SCREEN_WIDTH,
        "screen_height": SCREEN_HEIGHT,
        "fullscreen": FULLSCREEN
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la configuration : {e}")
