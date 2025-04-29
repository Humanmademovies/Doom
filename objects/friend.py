from objects.pnj import PNJ

class Friend(PNJ):
    def __init__(self, name, position=(0, 0, 0)):
        super().__init__(name=name, position=position)
        self.dialogue_enabled = True

    def update(self, player, delta_time, game_map):
        super().update(player, delta_time, game_map)
        if self.mode == "neutral":
            self._handle_dialogue(player)
        elif self.mode == "ally":
            self._assist_combat(player, delta_time, game_map)
        elif self.mode == "foe":
            self._attack_player(player, delta_time)

    def _handle_dialogue(self, player):
        if self.dialogue_enabled:
            self.set_action("idle")
            print(f"{self.sprite} vous salue.")
            self.dialogue_enabled = False

    def _assist_combat(self, player, delta_time, game_map):
        self.set_action("assist")
        # Placeholder

    def _attack_player(self, player, delta_time):
        self.set_action("attack")
        player.health -= 5 * delta_time
        print(f"{self.sprite} s'est retourné contre vous ! Santé du joueur : {int(player.health)}")
