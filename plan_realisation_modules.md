
# Plan de Réalisation des Modules Python

## 1. `main.py`
### Objectif :
Point d’entrée de l’application.

### Étapes de mise en œuvre :
- Importer `pygame`, `config`, `GameEngine` depuis `engine`.
- Initialiser Pygame et la fenêtre.
- Charger la configuration globale.
- Créer une instance de `GameEngine`.
- Démarrer la boucle principale (`engine.run()`).
- Gérer les exceptions (avec un bloc `try/except` autour de la boucle principale).

---

## 2. `config.py`
### Objectif :
Centraliser les paramètres globaux.

### Étapes de mise en œuvre :
- Définir les dimensions de la fenêtre (`SCREEN_WIDTH`, `SCREEN_HEIGHT`).
- Définir les paramètres de jeu (vitesse, FOV, distance de rendu...).
- Spécifier les chemins des assets (textures, sons).
- Ajouter un système de lecture/écriture depuis un fichier `.ini` ou `.json` si besoin d’une configuration modifiable.

---

## 3. `engine/game_engine.py`
### Objectif :
Coordonner toutes les composantes du jeu.

### Étapes de mise en œuvre :
- Créer une classe `GameEngine` avec les attributs :
  - `renderer`, `input_manager`, `world_map`, `player`, `enemies`, `items`.
- Méthodes :
  - `load_resources()`
  - `update(delta_time)`
  - `render()`
  - `run()` : boucle principale avec `while running`
- Gestion du framerate (`pygame.time.Clock`).

---

## 4. `engine/renderer.py`
### Objectif :
Rendu 3D avec PyOpenGL.

### Étapes de mise en œuvre :
- Initialiser OpenGL (perspective, viewport).
- Créer et lier les shaders.
- Charger les textures depuis `assets/textures/`.
- Gérer le rendu :
  - du sol et des murs (mesh générés depuis la map),
  - des sprites (billboarding : alignement face à la caméra).
- Utiliser `glDrawArrays`/`glDrawElements` pour le rendu.

---

## 5. `engine/input_manager.py`
### Objectif :
Gestion des entrées clavier/souris.

### Étapes de mise en œuvre :
- Capturer les événements Pygame.
- Traduire les touches `zqsd` en vecteurs de mouvement.
- Utiliser les mouvements de souris pour la rotation de la vue.
- Fournir une API : `get_movement_vector()`, `get_mouse_delta()`.

---

## 6. `world/map.py`
### Objectif :
Structure de la carte et génération de géométrie.

### Étapes de mise en œuvre :
- Représenter la carte avec un array 2D.
- Fournir une méthode pour charger une carte depuis un fichier texte ou JSON.
- Fonction `generate_geometry()` : retourne les positions des murs et sols pour le rendu.
- Associer les IDs aux textures murales ou de sol.

---

## 7. `world/level_generator.py`
### Objectif :
Génération dynamique ou procédurale.

### Étapes de mise en œuvre :
- Algorithmes de type :
  - Générateur de labyrinthe (DFS, Prim…),
  - Placement aléatoire d’ennemis et objets.
- Exporter la carte au format exploitable par `map.py`.

---

## 8. `objects/game_object.py`
### Objectif :
Classe de base des entités.

### Étapes de mise en œuvre :
- Attributs communs : position, direction, modèle 3D ou sprite.
- Méthodes virtuelles :
  - `update()`
  - `draw(renderer)`
- Préparer des hooks pour l’IA, l’interaction ou la physique.

---

## 9. `objects/player.py`
### Objectif :
Gestion du joueur.

### Étapes de mise en œuvre :
- Hériter de `GameObject`.
- Ajouter les attributs :
  - vie, niveau, statistiques, inventaire.
- Intégrer les entrées du joueur.
- Gérer les collisions et les interactions.

---

## 10. `objects/pnj.py`

### Objectif :

Définir une base commune pour tous les personnages non-joueurs.

### Étapes de mise en œuvre :

- Hériter de `GameObject`.
- Définir les attributs communs : position, sprite, visibilité, santé.
- Gérer un comportement neutre par défaut (`idle`).
- Fournir une méthode `update()` vide ou passive, destinée à être surchargée.

------

## 11. `objects/friend.py`

### Objectif :

Implémenter un PNJ non-hostile.

### Étapes de mise en œuvre :

- Hériter de `PNJ`.
- Ne pas attaquer le joueur.
- (Optionnel) Ajouter un comportement d'interaction ou de déplacement simple.
- Afficher un sprite distinct (`friend.png` ou équivalent).

------

## 12. `objects/foe.py`

### Objectif :

Implémenter un PNJ hostile (ancien comportement des ennemis).

### Étapes de mise en œuvre :

- Hériter de `PNJ`.
- Intégrer les décisions via `ai/behavior.py`.
- Implémenter les actions :
  - Suivre le joueur (`chase`)
  - Attaquer à proximité (`attack`)
- Gérer les collisions et la visibilité.

## 13. `objects/item.py`
### Objectif :
Objets interactifs.

### Étapes de mise en œuvre :
- Hériter de `GameObject`.
- Attributs : type (arme, potion…), effet associé.
- Déclenchement d’effet à la collecte (`on_pickup()`).
- Rendu en sprite face à la caméra.

---

## 14. `ai/behavior.py`
### Objectif :
Implémentation d’une IA simple.

### Étapes de mise en œuvre :
- Définir des classes ou fonctions pour différents comportements :
  - Patrouille, poursuite, attaque, fuite.
- Utiliser une machine à états :
  - Chaque ennemi suit un schéma décisionnel.
- Interfaces :
  - `decide_action(enemy, environment)`du

#### AJOUT AU PLAN DE RÉALISATION

## **15.** objects/weapon.py

### Objectif :

Représenter une arme équipable utilisée par le joueur.

### Étapes de mise en œuvre :

- Attributs : `name`, `weapon_type` ("melee", "ranged", etc.), `power`, `range`, `state`.
- Méthodes :
  - `set_state()` : pour définir l'état visuel (affichage HUD)
  - Intégration avec `Player.perform_attack()` pour appliquer les dégâts.
  - Associer un sprite à chaque état.

## **16.** objects/pnj.py

### Objectif :

Classe de base des personnages non-joueurs.

### Étapes de mise en œuvre :

- Lecture du fichier `config.json` dans le dossier `assets/pnj/<name>`.
- Initialiser la santé, les caractéristiques (P, S, I), le sprite et le mode.
- Gérer les dégâts reçus et changement d'état visuel.

## **17.** objects/friend.py

### Objectif :

Implémenter un PNJ non-hostile ou allié.

### Étapes de mise en œuvre :

- Méthode `update()` : dialogue, soutien en combat, trahison.
- Système de changement de mode dynamique (ally, foe).
- Sprite différent selon l'action.

## **18.** **objects/foe.py**

### Objectif :

PNJ hostile avec IA basée sur `behavior.py`

### Étapes de mise en œuvre :

- Méthode `update()` : appel à `decide_action()`.
- Routines : patrouille, poursuite, attaque.
- Vérification de ligne de vue avec `has_line_of_sight()`.
- Intégration dans le moteur de jeu avec déclenchement d'effet visuel (overlay).
