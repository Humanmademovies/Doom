# game_state_manager.py

class GameStateManager:
    """
    Gère une pile d'états de jeu (ex: menu, jeu, pause).
    Seul l'état au sommet de la pile est actif.
    """
    def __init__(self):
        self.states = []

    def push_state(self, state):
        """Ajoute un état au sommet de la pile."""
        self.states.append(state)

    def pop_state(self):
        """Retire l'état au sommet de la pile."""
        if self.states:
            self.states.pop()

    def switch_state(self, state):
        """Remplace tous les états actuels par un nouveau."""
        while self.states:
            self.states.pop()
        self.states.append(state)

    def get_active_state(self):
        """Retourne l'état actif, s'il y en a un."""
        return self.states[-1] if self.states else None

    def update(self, delta_time):
        """Met à jour l'état actif."""
        active_state = self.get_active_state()
        if active_state:
            active_state.update(delta_time)

    def render(self, screen):
        """Gère le rendu de l'état actif."""
        active_state = self.get_active_state()
        if active_state:
            active_state.render(screen)
