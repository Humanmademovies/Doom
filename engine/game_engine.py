# engine/game_engine.py

import pygame
from engine.input_manager import InputManager
from engine.renderer import Renderer
from world.map import GameMap
from objects.player import Player
from config import TARGET_FPS
from objects.foe import Foe

class GameEngine:
    def __init__(self, screen, map_path=None):

        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        # Composants du moteur
        self.input_manager = InputManager()
        self.renderer = Renderer(self.screen)
        self.game_map = GameMap()
        spawn_pos = self._find_free_cell()
        self.player = Player(position=(spawn_pos[0] + 0.5, 0.5, -spawn_pos[1] - 0.5))
        self.pnjs= []  # À remplir selon la carte ou le générateur
        self.items = []    # À remplir selon la carte ou le générateur

        self.load_resources()

    def load_resources(self):
        self.game_map.load_from_file("assets/maps/medium_map.json")
        self.pnjs = self.game_map.get_initial_pnjs()
        self.items = self.game_map.get_initial_items()
        self.renderer.load_textures()

    def update(self, delta_time):
        self.input_manager.update()
        move_vector = self.input_manager.get_movement_vector()
        mouse_delta = self.input_manager.get_mouse_delta()

        if self.input_manager.is_up_pressed():
            self.player.scroll_items(-1)
        elif self.input_manager.is_down_pressed():
            self.player.scroll_items(1)

        if self.input_manager.is_left_pressed():
            self.player.scroll_weapons(-1)
        elif self.input_manager.is_right_pressed():
            self.player.scroll_weapons(1)

        if self.input_manager.is_key_pressed(pygame.K_SPACE):
            self.player.use_selected_item()



        self.player.update(move_vector, mouse_delta, delta_time, self.game_map)

        if self.input_manager.is_mouse_pressed() and self.player.can_attack:
            self.player.perform_attack(self.pnjs, self.game_map)

        for pnj in self.pnjs:
            pnj.update(self.player, delta_time, self.game_map, self.renderer)


        for item in self.items:
            item.update(self.player)

    def render(self):
        self.renderer.clear()
        self.renderer.render_world(self.game_map)
        self.renderer.render_player(self.player)
        self.renderer.render_pnjs(self.pnjs)
        self.renderer.render_entities(self.items)
        self.renderer.render_hud(self.player, self.pnjs, self.items, self.game_map)
        self.renderer.swap_buffers()

    def _find_free_cell(self):
        for y, row in enumerate(self.game_map.grid):
            for x, cell in enumerate(row):
                if cell in self.game_map.floor_textures:
                    return (x, y)
        return (1, 1)


    def run(self):
        while self.running:
            delta_time = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update(delta_time)
            self.render()

    def _render_inventory(self, player):
        x_start = 20
        y_start = 60
        icon_size = 32
        spacing = 5

        # --- INVENTAIRE D'ITEMS (GAUCHE) ---
        for idx, item in enumerate(player.inventory_items):
            if item.item_type == "potion" and hasattr(item, "effect"):
                effect_type = item.effect.get("type")
                sprite_name = f"potion_{effect_type}.png"
            else:
                sprite_name = f"{item.item_type}.png"

            texture = self.textures.get(sprite_name)
            if not texture:
                print(f"[HUD] Texture manquante pour {sprite_name}")
                continue

            is_selected = (idx == player.item_index)
            scale = 1.2 if is_selected else 1.0
            size = int(icon_size * scale)
            x = x_start + idx * (icon_size + spacing)
            y = y_start - (size - icon_size) // 2

            glBindTexture(GL_TEXTURE_2D, texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + size, y)
            glTexCoord2f(1, 1); glVertex2f(x + size, y + size)
            glTexCoord2f(0, 1); glVertex2f(x, y + size)
            glEnd()

        # --- INVENTAIRE D'ARMES (DROITE) ---
        total = len(player.inventory_weapons)
        for idx, item in enumerate(player.inventory_weapons):
            name = item.weapon_attrs.get("name", "unknown") if hasattr(item, "weapon_attrs") else "unknown"
            sprite_name = f"weapon_{name}.png"
            texture = self.textures.get(sprite_name)
            if not texture:
                print(f"[HUD] Texture manquante pour {sprite_name}")
                continue

            is_selected = (idx == player.weapon_index)
            scale = 1.2 if is_selected else 1.0
            size = int(icon_size * scale)
            x = SCREEN_WIDTH - (total - idx) * (icon_size + spacing)
            y = y_start - (size - icon_size) // 2

            glBindTexture(GL_TEXTURE_2D, texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + size, y)
            glTexCoord2f(1, 1); glVertex2f(x + size, y + size)
            glTexCoord2f(0, 1); glVertex2f(x, y + size)
            glEnd()

            # Affichage des munitions si présentes
            ammo = getattr(item, "ammo", None)
            if ammo is not None:
                self._draw_text(f"x{ammo}", x + size + 2, y + size // 2 - 8)
