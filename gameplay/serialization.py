# gameplay/serialization.py

# On a besoin de connaître les classes que l'on pourrait avoir à recréer
from objects.player import Player
from objects.weapon import Weapon
from objects.item import Item
from objects.pnj import PNJ
from objects.friend import Friend
from objects.foe import Foe

# Un dictionnaire pour retrouver une classe à partir de son nom en chaîne de caractères
CLASS_MAP = {
    'Player': Player,
    'Weapon': Weapon,
    'Item': Item,
    'PNJ': PNJ,
    'Friend': Friend,
    'Foe': Foe
}


def serialize_object(obj, ignore_attrs=None):
    """
    Sérialise un objet en dictionnaire de manière récursive.
    """
    if ignore_attrs is None:
        ignore_attrs = []

    # Si l'objet est un type simple (incluant tuple), on le retourne tel quel
    if isinstance(obj, (int, float, str, bool, tuple)) or obj is None:
        return obj
    
    # Si c'est une liste, on sérialise chaque élément
    if isinstance(obj, list):
        return [serialize_object(item, ignore_attrs) for item in obj]
        
    # Si c'est un dictionnaire, on sérialise chaque valeur
    if isinstance(obj, dict):
        return {key: serialize_object(value, ignore_attrs) for key, value in obj.items()}

    # C'est un de nos objets custom, on utilise vars()
    data = {}
    try:
        data['__class__'] = obj.__class__.__name__ 
        
        attributes = vars(obj)
        for attr_name, attr_value in attributes.items():
            if attr_name not in ignore_attrs:
                data[attr_name] = serialize_object(attr_value, ignore_attrs)
    except TypeError:
        return obj
        
    return data

def deserialize_object(data):
    """
    CORRIGÉ: Désérialise des données (dictionnaire, liste, ou simple) pour recréer les objets Python.
    Utilise une copie des dictionnaires pour ne pas altérer les données source en mémoire.
    """
    # Si la donnée est une liste, on désérialise chaque élément.
    if isinstance(data, list):
        return [deserialize_object(item) for item in data]

    # Si ce n'est pas un dictionnaire, c'est une donnée simple (int, str...)
    if not isinstance(data, dict):
        return data

    # --- CORRECTION CRITIQUE : COPIE ---
    # On travaille sur une copie pour ne pas supprimer la clé '__class__' 
    # des données originales stockées dans la GameSession.
    data_copy = data.copy()

    # Vérifie si le dictionnaire contient une information de classe
    class_name = data_copy.pop('__class__', None)
    
    if class_name and class_name in CLASS_MAP:
        cls = CLASS_MAP[class_name]
        
        # On crée une instance "vide" de la classe pour éviter de lancer __init__
        obj = cls.__new__(cls)

        # On parcourt les données du dictionnaire pour remplir les attributs de l'objet
        for key, value in data_copy.items():
            setattr(obj, key, deserialize_object(value))
        return obj
    
    # Si ce n'est pas un de nos objets custom, c'est un dictionnaire normal
    return {key: deserialize_object(value) for key, value in data_copy.items()}
