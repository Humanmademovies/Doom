# states/base_state.py

class BaseState:
    """
    Classe de base abstraite pour tous les états de jeu.
    Chaque état (menu, jeu, pause) doit hériter de cette classe
    et implémenter ses propres méthodes update() et render().
    """
    def __init__(self, manager):
        self.manager = manager

    def update(self, delta_time):
        """
        Mise à jour de la logique de l'état.
        Doit être redéfinie dans les classes filles.
        """
        pass

    def render(self, screen):
        """
        Gère le rendu graphique de l'état.
        Doit être redéfinie dans les classes filles.
        """
        pass
