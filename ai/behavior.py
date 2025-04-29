# ai/behavior.py

def decide_action(enemy, player):
    """
    Détermine l'action actuelle d'un ennemi selon son état et l'environnement.
    Retourne une chaîne de caractères : 'idle', 'patrol', 'chase', 'attack'
    """
    if enemy.health <= 0:
        return "idle"

    distance = _distance(enemy.position, player.position)

    # Logique d'engagement
    if distance < 1.5:
        return "attack"
    elif distance < 6.0:
        return "chase"
    elif enemy.state in ("idle", "patrol"):
        return "patrol"
    else:
        return "idle"

def _distance(pos1, pos2):
    dx = pos1[0] - pos2[0]
    dz = pos1[2] - pos2[2]
    return (dx**2 + dz**2) ** 0.5
