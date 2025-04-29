class Weapon:
    def __init__(self, name="fist", weapon_type="melee", power=10, range=1.5):
        self.name = name
        self.weapon_type = weapon_type  # "melee", "ranged", etc.
        self.power = power              # dégâts
        self.range = range              # portée
        self.state = "idle"             # état d'animation : idle, walk, attack

    def set_state(self, state):
        if state in ("idle", "walk", "attack"):
            self.state = state
