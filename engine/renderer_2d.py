# engine/renderer_2d.py

import pygame
import os
from OpenGL.GL import *
from config import SCREEN_WIDTH, SCREEN_HEIGHT, LOGO_TARGET_SIZE, PLAYER_HEIGHT_IN_TILES, OVERWORLD_TILES_PER_SCREEN_HEIGHT
from world.sprite_analyzer import LOGO_SIZE

class Renderer2D:
    def __init__(self, screen):
        self.screen = screen
        self.textures = {}
        self.camera_x = 0
        self.camera_y = 0
        self.tile_size = SCREEN_HEIGHT / OVERWORLD_TILES_PER_SCREEN_HEIGHT

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        self._load_textures()

    def _load_textures(self):
        """Charge toutes les textures nécessaires au mode 2D."""
        for folder in ["assets/textures/", "assets/sprites/", "assets/pnj/"]:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith((".png", ".jpg", ".bmp")):
                        path = os.path.join(root, file)
                        try:
                            surface = pygame.image.load(path).convert_alpha()
                            
                            if 'building' in file:
                                scale_factor = LOGO_TARGET_SIZE / LOGO_SIZE
                                new_width = int(surface.get_width() * scale_factor)
                                new_height = int(surface.get_height() * scale_factor)
                                surface = pygame.transform.scale(surface, (new_width, new_height))
                                
                            image_data = pygame.image.tostring(surface, "RGBA", True)
                            width, height = surface.get_size()

                            texture_id = glGenTextures(1)
                            glBindTexture(GL_TEXTURE_2D, texture_id)
                            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

                            relative_path = os.path.relpath(path, "assets").replace("\\", "/")
                            self.textures[relative_path] = texture_id
                        except Exception as e:
                            print(f"Erreur chargement texture 2D : {file} -> {e}")

    def draw_map(self, game_map):
        """Dessine le calque du sol et des murs de la carte, gérant textures et couleurs."""
        
        for y, row in enumerate(game_map.grid):
            for x, cell in enumerate(row):
                if cell in game_map.floor_textures:
                    floor_data = game_map.floor_textures[cell]
                    
                    if isinstance(floor_data, str):
                        texture_id = self.textures.get(f"textures/{floor_data}")
                        if texture_id:
                            self._draw_quad_with_texture(
                                (x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y),
                                (self.tile_size, self.tile_size),
                                texture_id
                            )
                    elif isinstance(floor_data, (list, tuple)):
                        self._draw_colored_quad(
                            (x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y),
                            (self.tile_size, self.tile_size),
                            floor_data
                        )

    def draw_sprites(self, sprites):
        """Dessine une liste de sprites (joueur, PNJ, objets) décalée par la caméra."""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        for sprite_data in sprites:
            position = sprite_data["position"]
            texture_name = sprite_data["texture"]
            size = sprite_data.get("size", self.tile_size)
            
            texture_id = self.textures.get(texture_name)
            if not texture_id:
                print(f"Sprite non trouvé pour le rendu 2D : {texture_name}")
                continue

            self._draw_quad_with_texture(
                (position[0] - size/2 - self.camera_x, position[1] - size/2 - self.camera_y),
                (size, size),
                texture_id
            )

        glDisable(GL_BLEND)

    def _draw_quad_with_texture(self, position, size, texture_id):
        x, y = position
        width, height = size

        glBindTexture(GL_TEXTURE_2D, texture_id)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 0); glVertex2f(x, y + height)
        glEnd()

    def _draw_colored_quad(self, position, size, color):
        x, y = position
        width, height = size
        r, g, b = color

        glDisable(GL_TEXTURE_2D)
        glColor3f(r / 255.0, g / 255.0, b / 255.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        glColor3f(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)

    def update_camera(self, target_position, map_size):
        map_width_pixels = map_size[0] * self.tile_size
        map_height_pixels = map_size[1] * self.tile_size
        
        target_x_pixels = target_position[0] * self.tile_size
        target_y_pixels = target_position[1] * self.tile_size
        
        self.camera_x = target_x_pixels - SCREEN_WIDTH / 2
        self.camera_y = target_y_pixels - SCREEN_HEIGHT / 2
        
        self.camera_x = max(0, min(self.camera_x, map_width_pixels - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, map_height_pixels - SCREEN_HEIGHT))
