Here's the updated `plan_realisation_modules.md`, focusing only on the work that still needs to be done or modified, based on the current state of the repository.



# Plan de Réalisation Technique des Modules



Ce document détaille les étapes d'implémentation restantes pour faire évoluer le projet vers son architecture finale.

------



## Phase 2 : Le Monde Extérieur (Overworld)



**Objectif :** Développer le mode de jeu en 2D vue de dessus.



### 1. Création de l'État du Monde Extérieur



- **Fichier à créer :** `states/overworld_state.py`
- **Détails d'implémentation :**
  - Créer une classe `OverworldState` qui hérite de `BaseState`.
  - `__init__()`: Chargera une carte spécifique au monde 2D.
  - `update()`: Gérera la logique de déplacement du joueur en 2D et les interactions.
  - `render()`: Fera appel à un nouveau moteur de rendu 2D.



### 2. Création du Moteur de Rendu 2D



- **Fichier à créer :** `engine/renderer_2d.py`
- **Détails d'implémentation :**
  - Ce sera une classe `Renderer2D` beaucoup plus simple que le renderer 3D.
  - Elle utilisera principalement `pygame.draw` et `screen.blit`.
  - Méthodes à créer :
    - `draw_map(map_data)`: Dessine le sol et les obstacles à partir d'un tileset.
    - `draw_sprite(sprite, position)`: Dessine le joueur, les PNJ, etc.
    - Gérera une caméra 2D qui suit le joueur.



### 3. Adaptation de l'Objet `Player`



- **Fichier à modifier :** `objects/player.py`
- **Détails d'implémentation :**
  - La classe `Player` devra gérer un état interne (`self.mode = "3D"` ou `"2D"`).
  - La méthode `update` devra avoir une branche : `if self.mode == "3D": ... else: ...`.
  - La logique de mouvement 2D sera plus simple (4 ou 8 directions).

------



## Phase 3 : Transitions et Persistance des Données



**Objectif :** Permettre au joueur de passer de la 2D à la 3D de manière fluide, en conservant ses données.



### 1. Création d'un Objet de Session



- **Fichier à créer :** `gameplay/game_session.py`
- **Détails d'implémentation :**
  - Créer une classe `GameSession` (ou un simple dictionnaire) qui stockera toutes les données persistantes du joueur :
    - Santé, inventaire, munitions (`ammo_pool`).
    - Quêtes actives.
    - Position du joueur dans le monde 2D.
  - Cette instance sera créée au début d'une "Nouvelle Partie" et passée en paramètre à chaque nouvel état.



### 2. Implémentation des Points de Transition



- **Fichier à modifier :** `world/map.py`
- **Détails d'implémentation :**
  - Ajouter une nouvelle section dans les JSON des cartes 2D : `"transitions": [{"x": 10, "y": 15, "target_map": "...", "target_state": "InteriorState"}]`.
  - Dans `OverworldState.update()`, vérifier si le joueur se trouve sur une tuile de transition.
  - Si oui, appeler `self.manager.switch_state(InteriorState(map_path=..., session=...))`.
  - Faire la même chose pour sortir d'un intérieur et revenir au monde 2D.



### 3. Sauvegarde et Chargement



- **Fichiers à modifier :** `GameStateManager` et `MenuState`.
- **Détails d'implémentation :**
  - Activer les boutons "Sauvegarder" et "Charger" dans le menu principal pour appeler les méthodes correspondantes dans le `GameStateManager`.

------



## Phase 4 : Systèmes de Gameplay Avancés



**Objectif :** Donner de la profondeur au jeu avec des quêtes et des dialogues dynamiques.



### 1. Gestionnaire de Quêtes



- **Fichier à créer :** `gameplay/quest_manager.py`
- **Détails d'implémentation :**
  - Créer une classe `QuestManager`.
  - Une instance sera stockée dans l'objet `GameSession`.
  - Une quête sera un objet avec un `id`, un `titre`, une `description`, et une liste d'objectifs (triggers).
  - Créer une méthode `notify(event_type, target_id)`.



### 2. Gestionnaire de Dialogue



- **Fichier à créer :** `gameplay/dialogue_manager.py`
- **Détails d'implémentation :**
  - Créer une classe `DialogueManager`.
  - Quand le joueur interagit avec un PNJ, un `DialogueState` sera poussé sur la pile du `GameStateManager`.
  - Cet état affichera une interface de dialogue.
  - **Intégration d'Ollama :** Utiliser la librairie `requests` pour faire un appel POST à l'API locale d'Ollama. Afficher un indicateur de chargement pendant l'attente de la réponse.

------



## Améliorations de l'existant





### 1. `objects/weapon.py`



- **Fichiers à modifier :** `objects/weapon.py`, `objects/player.py`, `engine/input_manager.py`.
- **Détails d'implémentation :**
  - Ajouter un attribut `fire_mode` (`"semi"`, `"auto"`) à la classe `Weapon`.
  - Créer une méthode `switch_fire_mode()` dans la classe `Weapon`.
  - Modifier `InputManager` pour distinguer `is_mouse_clicked()` (pour le mode "semi") et `is_mouse_held()` (pour le mode "auto").
  - Adapter la logique de tir dans `Player` et `GameEngine` en conséquence.



### 2. `objects/player.py`



- **Fichiers à modifier :** `objects/player.py`
- **Détails d'implémentation :**
  - Implémenter une limite d'inventaire de 4 armes maximum.
  - Si le joueur ramasse une nouvelle arme alors que l'inventaire est plein, l'arme actuellement tenue doit être "droppée" sur la carte.