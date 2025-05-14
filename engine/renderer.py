# engine/renderer.py

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FOV, NEAR_CLIP, FAR_CLIP, BACKGROUND_COLOR, TEXTURES_PATH
import os
import pygame.freetype  # en haut du fichier
from PIL import Image
import numpy as np

class Renderer:
    def __init__(self, screen):
        self.damage_overlay_timer = 0.0
        self.screen = screen
        self._init_opengl()
        self.textures = {}
        self.font = pygame.freetype.Font("assets/ui/PressStart2P-Regular.ttf", 16)

    def _init_opengl(self):
        glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, SCREEN_WIDTH / SCREEN_HEIGHT, NEAR_CLIP, FAR_CLIP)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_TEXTURE_2D)
        glClearColor(*BACKGROUND_COLOR)

    def load_textures(self):
        for folder in [TEXTURES_PATH, "assets/sprites/", "assets/pnj/", "assets/ui/", "assets/weapons/"]:
            for root, _, files in os.walk(folder):
                for file in files:
                    if not file.lower().endswith((".png", ".jpg", ".bmp")):
                        continue
          
                    path = os.path.join(root, file)
                    try:
                        texture_id = self._load_texture(path)
                        relative_path = os.path.relpath(path, "assets").replace("\\", "/")
                        self.textures[relative_path] = texture_id
                        path = os.path.join(root, file)
                        self.textures[file] = texture_id


                        print(f"Texture chargée : {file} → ID OpenGL : {texture_id}")
                    except Exception as e:
                        print(f"Erreur chargement texture : {file} → {e}")



    def _draw_text(self, text, x, y):
        # Rendre le texte sur une surface Pygame avec antialiasing (blanc sur transparent)
        surface, _ = self.font.render(text, (255, 255, 255))

        # Convertir la surface en chaîne de bytes pour OpenGL (format RGBA)
        texture_data = pygame.image.tostring(surface, "RGBA", True)

        # Obtenir les dimensions de la surface (en pixels)
        width, height = surface.get_size()

        # Générer une nouvelle texture OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Charger les données de la surface dans OpenGL
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

        # Appliquer un filtrage linéaire pour lisser la texture
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        # Activer la texturation 2D
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Rendu de la texture avec inversion horizontale et verticale via coordonnées UV inversées
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)                      # coin supérieur gauche
        glTexCoord2f(1, 1); glVertex2f(x + width, y)              # coin supérieur droit
        glTexCoord2f(1, 0); glVertex2f(x + width, y + height)     # coin inférieur droit
        glTexCoord2f(0, 0); glVertex2f(x, y + height)             # coin inférieur gauche
        glEnd()
        glDeleteTextures(int(texture_id))

        # Nettoyage : suppression de la texture temporaire
        #glDeleteTextures(texture_id)




    def _load_texture(self, path):
        

        surface = pygame.image.load(path)
        image_data = pygame.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture_id

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        

    def render_world(self, game_map):
       
        for wall in game_map.get_wall_geometry():
            self._draw_quad(wall["vertices"], wall["texture"])

        for floor in game_map.get_floor_geometry():
            self._draw_quad(floor["vertices"], floor["texture"])


    def render_player(self, player):
        glLoadIdentity()

        x, y, z = player.position
        self.camera_position = player.position  # Enregistrement pour tri des entités

        glRotatef(-player.rotation_y, 0, 1, 0)
        glTranslatef(-x, -y, -z)


    def render_pnjs(self, pnjs):
        from operator import itemgetter

        # Accès à la position caméra (le joueur doit avoir été rendu avant)
        try:
            cam_x, _, cam_z = self.camera_position  # doit être défini par render_player
        except AttributeError:
            cam_x, cam_z = 0.0, 0.0  # fallback si non défini

        # Tri des PNJ par distance (du plus éloigné au plus proche)
        sorted_pnjs = sorted(
            pnjs,
            key=lambda p: (p.position[0] - cam_x) ** 2 + (p.position[2] - cam_z) ** 2,
            reverse=True
        )

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(False)

        for pnj in sorted_pnjs:
            pnj.draw(self)

        glDepthMask(True)


    def render_entities(self, entities):
        try:
            cam_x, _, cam_z = self.camera_position
        except AttributeError:
            cam_x, cam_z = 0.0, 0.0

        sorted_entities = sorted(
            entities,
            key=lambda e: (e.position[0] - cam_x) ** 2 + (e.position[2] - cam_z) ** 2,
            reverse=True
        )

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(False)

        for entity in sorted_entities:
            entity.draw(self)

        glDepthMask(True)


    def _draw_quad(self, vertices, texture_name):
     
        texture_id = self.textures.get(texture_name)
        if texture_id is None:
            print("Texture introuvable :", texture_name)
            return

        glBindTexture(GL_TEXTURE_2D, texture_id)
        glBegin(GL_QUADS)
        for i, (x, y, z) in enumerate(vertices):
            u = (i == 1 or i == 2)
            v = (i == 2 or i == 3)
            glTexCoord2f(u, v)
            glVertex3f(x, y, z)
        glEnd()

    def swap_buffers(self):
        pygame.display.flip()

    def draw_sprite(self, position, texture_name, size=0.4):
        """
        Rendu d’un sprite orienté vers la caméra (billboarding).
        - `position` : (x, y, z)
        - `texture_name` : nom du fichier déjà chargé dans self.textures
        - `size` : demi-largeur/hauteur du sprite
        """
        texture_id = self.textures.get(texture_name)
        if texture_id is None:
            return


        glBindTexture(GL_TEXTURE_2D, texture_id)
        glPushMatrix()

        # Placement dans le monde
        glTranslatef(*position)

        # Orientation automatique : face à la caméra (vue à la 1ère personne)
        # On suppose que la caméra ne tourne que horizontalement (axe Y)
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        right = [modelview[0][0], modelview[1][0], modelview[2][0]]
        up = [modelview[0][1], modelview[1][1], modelview[2][1]]

        # Dessin manuel des 4 sommets avec billboarding
        glBegin(GL_QUADS)
        for dx, dy, u, v in [(-1, -1, 0, 0), (1, -1, 1, 0), (1, 1, 1, 1), (-1, 1, 0, 1)]:
            x = right[0] * dx * size + up[0] * dy * size
            y = right[1] * dx * size + up[1] * dy * size
            z = right[2] * dx * size + up[2] * dy * size
            glTexCoord2f(u, v)
            glVertex3f(x, y, z)
        glEnd()

        glPopMatrix()

    def render_hud(self, player, pnjs, items, game_map):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        self._render_health_bar(player)
        self._draw_text(f"Santé : {int(player.health)} / 100", 20, 45)

        self._render_mini_map(player, pnjs, game_map)
        self._render_inventory(player)
        self.render_weapon_hud(player)

        glEnable(GL_DEPTH_TEST)
        if self.damage_overlay_timer > 0:
            self.damage_overlay_timer -= 1/60  # supposer 60 FPS, sinon utiliser delta_time
            self._render_damage_overlay()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def _render_health_bar(self, player):
        texture = self.textures.get("life.png")
        if not texture:
            return

        total_levels = 6
        full_width = 200
        full_height = 20
        x, y = 20, 20

        # Calcul de l’indice de segment (de 0 = pleine santé à 5 = zéro santé)
        health_ratio = max(0.0, min(player.health / 100, 1.0))
        level_index = round((1.0 - health_ratio) * (total_levels - 1))

        segment_height = 1.0 / total_levels
        uv_y0 = level_index * segment_height
        uv_y1 = uv_y0 + segment_height

        glBindTexture(GL_TEXTURE_2D, texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, uv_y1)
        glVertex2f(x, y)
        glTexCoord2f(1.0, uv_y1)
        glVertex2f(x + full_width, y)
        glTexCoord2f(1.0, uv_y0)
        glVertex2f(x + full_width, y + full_height)
        glTexCoord2f(0.0, uv_y0)
        glVertex2f(x, y + full_height)
        glEnd()



    def _render_mini_map(self, player, pnjs, game_map):
        tile_size = 4
        map_offset_x = SCREEN_WIDTH - len(game_map.grid[0]) * tile_size - 20
        map_offset_y = 20

        for y, row in enumerate(game_map.grid):
            for x, cell in enumerate(row):
                color = (0.2, 0.2, 0.2) if cell in game_map.wall_textures else (0.6, 0.6, 0.6)
                self._draw_rect_2d(map_offset_x + x * tile_size, map_offset_y + y * tile_size, tile_size, tile_size, color)

        # Joueur = bleu
        px = int(player.position[0])
        py = int(-player.position[2])
        self._draw_rect_2d(map_offset_x + px * tile_size, map_offset_y + py * tile_size, tile_size, tile_size, (0.0, 0.4, 1.0))

        # PNJ
        for pnj in pnjs:
            px = int(pnj.position[0])
            py = int(-pnj.position[2])
            color = (0.0, 1.0, 0.0) if pnj.mode == "friend" else (1.0, 0.0, 0.0)
            self._draw_rect_2d(map_offset_x + px * tile_size, map_offset_y + py * tile_size, tile_size, tile_size, color)

    def _render_inventory(self, player):


        x_start = 20
        y_start = 60
        icon_size = 32
        spacing = 5
       

        for idx, item in enumerate(player.inventory_items):
            if item.item_type == "potion" and hasattr(item, "effect"):
                effect_type = item.effect.get("type")
                sprite_name = f"potion_{effect_type}.png"
            elif item.item_type == "weapon" and hasattr(item, "weapon_attrs"):
                name = item.weapon_attrs.get("name", "unknown")
                sprite_name = f"weapon_{name}.png"
            else:
                sprite_name = f"{item.item_type}.png"

            texture = self.textures.get(sprite_name)
            if not texture:
              #  print(f"[HUD] Texture manquante pour {sprite_name}")
                continue


            is_selected = (idx == player.inventory_index)
            scale = 1.2 if is_selected else 1.0
            size = int(icon_size * scale)
            x = x_start + idx * (icon_size + spacing)
            y = y_start - (size - icon_size) // 2  # recentrer verticalement
            #print(f"[HUD] item: {item.id}, type: {item.item_type}, weapon_attrs: {getattr(item, 'weapon_attrs', None)}")

            glBindTexture(GL_TEXTURE_2D, texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(x, y)
            glTexCoord2f(1, 0)
            glVertex2f(x + size, y)
            glTexCoord2f(1, 1)
            glVertex2f(x + size, y + size)
            glTexCoord2f(0, 1)
            glVertex2f(x, y + size)
            glEnd()


    def _draw_rect_2d(self, x, y, w, h, color):
        glDisable(GL_TEXTURE_2D)
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        glColor3f(1, 1, 1)
        glEnable(GL_TEXTURE_2D)

    def _render_damage_overlay(self):
        texture = self.textures.get("blood_overlay.png")
        if not texture:
            return

        glPushAttrib(GL_ENABLE_BIT)            # Sauvegarde de l’état OpenGL
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(SCREEN_WIDTH, 0)
        glTexCoord2f(1, 1); glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
        glTexCoord2f(0, 1); glVertex2f(0, SCREEN_HEIGHT)
        glEnd()

        glPopAttrib()                          # Restauration de l’état précédent

    def render_weapon_hud(self, player):
        weapon = player.active_weapon
        sprite_path = f"weapons/{weapon.name}/{weapon.name}_{weapon.state}.png"
        # Détermination dynamique du sprite
        texture_id = self.textures.get(sprite_path)
        if not texture_id:
            return

        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Récupération de la taille de la texture à partir d'OpenGL
        width = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
        height = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)

        # Hauteur cible = 2/3 de l'écran, largeur proportionnelle
        target_height = int(SCREEN_HEIGHT * 2 / 3)
        scale = target_height / height
        target_width = int(width * scale)

        x = (SCREEN_WIDTH - target_width) // 2
        y = SCREEN_HEIGHT - target_height

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)                             # bas gauche
        glTexCoord2f(1, 1); glVertex2f(x + target_width, y)             # bas droit
        glTexCoord2f(1, 0); glVertex2f(x + target_width, y + target_height)  # haut droit
        glTexCoord2f(0, 0); glVertex2f(x, y + target_height)            # haut gauche
        glEnd()

        glDisable(GL_BLEND)


