# Plan de Réalisation Technique des Modules

Ce document sert de feuille de route technique pour le développement du projet. Il détaille le rôle de chaque module, son implémentation actuelle et les fonctionnalités futures à intégrer.

---

## 1. `config.py`
### Objectif :
Centraliser tous les paramètres globaux et les constantes d'équilibrage pour faciliter la maintenance et les ajustements.

### Implémentation :
- Définit les constantes de base (fenêtre, vitesse du joueur, sensibilité).
- Spécifie les chemins vers les ressources (`assets`).
- **Constante `WEAPON_CONFIG`**: Un dictionnaire central qui contient toutes les statistiques des armes (dégâts, portée, cadence, taille du chargeur, type de munitions). C'est le point de contrôle principal pour l'équilibrage du jeu.
- **Constante `DEFAULT_MAP`**: Définit la carte à charger par défaut au lancement du jeu.

---

## 2. `engine/input_manager.py`
### Objectif :
Abstraire et gérer toutes les entrées du joueur (clavier et souris) de manière claire et exploitable par le moteur.

### Implémentation :
- Gère les mouvements (`ZQSD`) en les traduisant en un vecteur de déplacement.
- Gère le mouvement de la souris pour la rotation de la caméra.
- Gère les appuis uniques sur les touches directionnelles pour la navigation dans l'inventaire.
- **Distinction du clic souris** :
    - `is_mouse_held()` : Renvoie `True` tant que le bouton est maintenu (pour le tir automatique).
    - `is_mouse_clicked()` : Renvoie `True` uniquement à la frame où le bouton est pressé (pour le tir semi-automatique ou les interactions).

---

## 3. `engine/game_engine.py`
### Objectif :
Orchestrer le cycle de vie du jeu, en coordonnant les mises à jour, le rendu et les interactions entre les différents modules.

### Implémentation :
- Gère la boucle de jeu principale (`run()`) et le timing (`delta_time`).
- Initialise et charge toutes les ressources nécessaires au démarrage (`load_resources`).
- **Boucle `update(delta_time)`** :
    - Met à jour l'état des entrées via `input_manager`.
    - Gère les actions du joueur qui ne sont pas liées au tir (défilement d'inventaire, utilisation d'objets).
    - Appelle `player.update()` pour gérer le mouvement.
    - **Déclenche le tir** en appelant `player.fire()` si la souris est maintenue.
    - **Déclenche le rechargement** en appelant `player.reload_weapon()` sur appui de la touche 'R'.
    - Met à jour tous les PNJ et les items présents sur la carte.
- **Boucle `render()`** : Appelle les différentes méthodes du `renderer` pour afficher le monde, les entités et le HUD.

---

## 4. `engine/renderer.py`
### Objectif :
Gérer tout l'aspect visuel du jeu, du rendu 3D du monde à l'interface utilisateur 2D (HUD).

### Implémentation :
- Initialise OpenGL et la perspective de la caméra.
- Charge et stocke toutes les textures du jeu (`load_textures`).
- **Rendu du monde** : Affiche la géométrie des murs et des sols générée par `GameMap`.
- **Rendu des entités** : Affiche les PNJ et les items en tant que sprites 2D dans l'espace 3D (billboarding).
- **Rendu du HUD (`render_hud`)** :
    - Affiche la barre de vie et la mini-carte.
    - Affiche l'inventaire des objets et des armes.
    - Affiche l'arme tenue par le joueur.
    - **Affiche les informations sur les munitions** : utilise une méthode dédiée (`_render_ammo_info`) pour montrer les munitions dans le chargeur et la réserve totale, en lisant les données directement depuis l'arme active et le `ammo_pool` du joueur.

---

## 5. `objects/weapon.py`
### Objectif :
Définir le comportement, les statistiques et l'état de chaque arme du jeu. C'est une classe fondamentale du gameplay.

### Implémentation :
- **Attributs** : `name`, `weapon_type`, `power`, `range`, `rpm` (cadence), `mag_size` (taille chargeur), `ammo_loaded` (munitions actuelles), `ammo_type`.
- **Gestion de la cadence** : Un `attack_timer` interne, basé sur le `fire_rate` (calculé depuis les RPM), empêche de tirer plus vite que prévu.
- **`perform_attack()`** : Méthode centrale qui vérifie si l'arme peut tirer (cadence + munitions), décrémente les munitions et réinitialise le timer.
- **`reload(ammo_pool)`** : Logique de rechargement qui calcule les munitions nécessaires et les puise dans le pool de munitions fourni par le joueur.
- **`set_state()`** : Permet de changer l'état de l'arme (`idle`, `attack`), utilisé pour les animations du HUD.

### À implémenter :
- **Attribut `fire_mode`** (`"semi"`, `"auto"`) pour gérer différents comportements de tir.
- **Méthode `switch_fire_mode()`** pour permettre au joueur de changer le mode de tir des armes compatibles.

---

## 6. `objects/player.py`
### Objectif :
Représenter le joueur, ses statistiques, ses actions et son inventaire.

### Implémentation :
- Gère la santé, la position et la rotation de la caméra.
- **`ammo_pool`** : Dictionnaire qui centralise toutes les munitions possédées par le joueur, partagées entre les armes du même calibre.
- **`fire(pnjs, game_map)`** : Méthode principale de tir. Elle appelle `active_weapon.perform_attack()` et, si le tir réussit, effectue une détection de cible (`_is_in_view`, `_has_line_of_sight`) pour appliquer les dégâts.
- **`reload_weapon()`** : Appelle la méthode `reload()` de l'arme active en lui passant son propre `ammo_pool`.
- **`pickup_weapon(item)`** et **`add_ammo(type, amount)`** : Méthodes spécialisées pour gérer le ramassage d'armes et de munitions, appelées par `item.on_pickup()`.

### À implémenter :
- **Limite d'inventaire** : Gérer une limite de 4 armes maximum. Si le joueur en ramasse une nouvelle alors que son inventaire est plein, l'arme actuelle est "droppée" sur la carte.

---

## 7. `objects/item.py`
### Objectif :
Définir les objets ramassables dans le monde du jeu.

### Implémentation :
- **Constructeur flexible** : Peut créer des potions (`effect`), des armes (`weapon_attrs`) ou des munitions (`ammo_attrs`).
- **`on_pickup(player)`** : Agit comme un **aiguillage intelligent**. Plutôt que de contenir la logique, elle appelle la méthode appropriée du joueur (`player.pickup_weapon()`, `player.add_ammo()`, `player.add_to_inventory()`), ce qui rend le code plus modulaire.

---

## 8. `world/map.py`
### Objectif :
Charger, représenter et fournir la géométrie d'un niveau.

### Implémentation :
- Charge les données d'un niveau depuis un fichier JSON (`map`, `wall_textures`, `floor_textures`, `foes`, `friends`, `items`).
- **`get_wall_geometry()` / `get_floor_geometry()`** : Génère les coordonnées des polygones pour les murs et les sols, utilisés par le `renderer`.
- **`get_initial_pnjs()` / `get_initial_items()`** : Instancie les objets `Foe`, `Friend` et `Item` à partir des données de la carte.

---

## 9. `world/level_generator.py`
### Objectif :
Génération dynamique ou procédurale.

### Étapes de mise en œuvre :
- Algorithmes de type :
  - Générateur de labyrinthe (DFS, Prim…),
  - Placement aléatoire d’ennemis et objets.
- Exporter la carte au format exploitable par `map.py`.

---

## 10. `objects/game_object.py`
### Objectif :
Classe de base des entités.

### Étapes de mise en œuvre :
- Attributs communs : position, direction, modèle 3D ou sprite.
- Méthodes virtuelles :
  - `update()`
  - `draw(renderer)`
- Préparer des hooks pour l’IA, l’interaction ou la physique.

---

## 11. `objects/player.py`
### Objectif :
Gestion du joueur.

### Étapes de mise en œuvre :
- Hériter de `GameObject`.
- Ajouter les attributs :
  - vie, niveau, statistiques, inventaire.
- Intégrer les entrées du joueur.
- Gérer les collisions et les interactions.

---

## 12. `objects/pnj.py`

### Objectif :

Définir une base commune pour tous les personnages non-joueurs.

### Étapes de mise en œuvre :

- Hériter de `GameObject`.
- Définir les attributs communs : position, sprite, visibilité, santé.
- Gérer un comportement neutre par défaut (`idle`).
- Fournir une méthode `update()` vide ou passive, destinée à être surchargée.

------

## 13. `objects/friend.py`

### Objectif :

Implémenter un PNJ non-hostile.

### Étapes de mise en œuvre :

- Hériter de `PNJ`.
- Ne pas attaquer le joueur.
- (Optionnel) Ajouter un comportement d'interaction ou de déplacement simple.
- Afficher un sprite distinct (`friend.png` ou équivalent).

------

## 14. `objects/foe.py`

### Objectif :

Implémenter un PNJ hostile (ancien comportement des ennemis).

### Étapes de mise en œuvre :

- Hériter de `PNJ`.
- Intégrer les décisions via `ai/behavior.py`.
- Implémenter les actions :
  - Suivre le joueur (`chase`)
  - Attaquer à proximité (`attack`)
- Gérer les collisions et la visibilité.

## 15. `objects/item.py`
### Objectif :
Objets interactifs.

### Étapes de mise en œuvre :
- Hériter de `GameObject`.
- Attributs : type (arme, potion…), effet associé.
- Déclenchement d’effet à la collecte (`on_pickup()`).
- Rendu en sprite face à la caméra.

---

## 16. `ai/behavior.py`
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

## **16.** objects/weapon.py

### Objectif :

Représenter une arme équipable utilisée par le joueur.

### Étapes de mise en œuvre :

- Attributs : `name`, `weapon_type` ("melee", "ranged", etc.), `power`, `range`, `state`.
- Méthodes :
  - `set_state()` : pour définir l'état visuel (affichage HUD)
  - Intégration avec `Player.perform_attack()` pour appliquer les dégâts.
  - Associer un sprite à chaque état.

## **17.** objects/pnj.py

### Objectif :

Classe de base des personnages non-joueurs.

### Étapes de mise en œuvre :

- Lecture du fichier `config.json` dans le dossier `assets/pnj/<name>`.
- Initialiser la santé, les caractéristiques (P, S, I), le sprite et le mode.
- Gérer les dégâts reçus et changement d'état visuel.

## **18.** objects/friend.py

### Objectif :

Implémenter un PNJ non-hostile ou allié.

### Étapes de mise en œuvre :

- Méthode `update()` : dialogue, soutien en combat, trahison.
- Système de changement de mode dynamique (ally, foe).
- Sprite différent selon l'action.

## **19.** **objects/foe.py**

### Objectif :

PNJ hostile avec IA basée sur `behavior.py`

### Étapes de mise en œuvre :

- Méthode `update()` : appel à `decide_action()`.
- Routines : patrouille, poursuite, attaque.
- Vérification de ligne de vue avec `has_line_of_sight()`.
- Intégration dans le moteur de jeu avec déclenchement d'effet visuel (overlay).
