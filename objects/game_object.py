# objects/game_object.py

from abc import ABC, abstractmethod

class GameObject(ABC):
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=0.0):
        self.position = list(position)
        self.rotation = rotation  # Orientation horizontale (en degrés ou radians selon l’usage)
        self.visible = True       # Permet de désactiver le rendu si nécessaire

    @abstractmethod
    def update(self, *args, **kwargs):
        """
        Méthode de mise à jour appelée à chaque frame.
        Doit être redéfinie dans les classes dérivées.
        """
        pass

    @abstractmethod
    def draw(self, renderer):
        """
        Méthode d’affichage OpenGL.
        Chaque objet est responsable de son rendu (souvent un sprite billboard).
        """
        pass
