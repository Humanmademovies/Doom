# Feuille de Route Technique - Projet "Doom Gemini"

Ce document détaille l'architecture et les étapes d'implémentation pour faire évoluer le projet d'un simple FPS "Doom-like" vers un jeu hybride 2D/3D avec des systèmes de quêtes et de dialogue avancés.

## Plan : Architecture Modulaire et Évolutive

### Structure des Dossiers

```plaintext
doom_project/
├── main.py                     # Point d'entrée : lance le GameStateManager
├── game_state_manager.py       # NOUVEAU: Chef d'orchestre, gère les états de jeu
├── config.py
│
├── states/                     # NOUVEAU: Dossier pour chaque mode de jeu
│   ├── __init__.py
│   ├── base_state.py           # Classe de base pour tous les états
│   ├── menu_state.py           # Gère le menu principal (UI, boutons)
│   ├── overworld_state.py      # Gère le gameplay en 2D (vue de dessus)
│   └── interior_state.py       # Encapsule le moteur 3D pour les niveaux "Doom-like"
│
├── gameplay/                   # NOUVEAU: Dossier pour la logique de jeu avancée
│   ├── __init__.py
│   ├── quest_manager.py        # Suivi des quêtes et de leurs objectifs (triggers)
│   └── dialogue_manager.py     # Gère les conversations et les appels à l'IA (Ollama)
│
├── engine/
│   ├── __init__.py
│   ├── game_engine.py          # Rôle adapté : cœur du mode de jeu 3D (InteriorState)
│   ├── renderer.py             # Moteur de rendu 3D
│   ├── renderer_2d.py          # NOUVEAU: Moteur de rendu 2D pour le mode Overworld
│   └── input_manager.py
│
├── world/
│   ├── __init__.py
│   ├── map.py
│   └── level_generator.py
│
├── objects/
│   ├── __init__.py
│   ├── game_object.py
│   ├── player.py               # Rôle étendu pour gérer les modes 2D/3D
│   ├── pnj.py
│   ├── friend.py
│   ├── foe.py
│   ├── weapon.py
│   └── item.py
│
├── ai/
│   ├── __init__.py
│   └── behavior.py
│
└── assets/
    ├── textures/
    ├── sprites/
    ├── maps/
    └── ...
```

---

## Phase 0 : Refactorisation pour une Architecture à États (La Fondation)

**Objectif :** Transformer l'architecture monolithique actuelle en une machine à états flexible. C'est l'étape la plus cruciale pour permettre l'ajout de nouvelles fonctionnalités (menu, mode 2D) sans casser la logique 3D existante.

### 1. Création du Gestionnaire d'États (`GameStateManager`)
-   **Fichier à créer :** `game_state_manager.py`
-   **Détails d'implémentation :**
    -   Créer une classe `GameStateManager`.
    -   Elle contiendra une pile d'états : `self.states = []`.
    -   Méthodes à créer :
        -   `push_state(state)`: Ajoute un état au sommet de la pile (ex: ouvrir un menu pause).
        -   `pop_state()`: Retire l'état actuel.
        -   `switch_state(state)`: Remplace toute la pile par un nouvel état (ex: passer du menu au jeu).
        -   `update()` et `render()`: Appellent les méthodes correspondantes de l'état actif (celui au sommet de la pile).

### 2. Création de la Structure des États
-   **Fichier à créer :** `states/base_state.py`
-   **Détails d'implémentation :**
    -   Créer une classe de base abstraite `BaseState`.
    -   Elle définira les méthodes que tous les états devront implémenter : `__init__(self, manager)`, `update(self, delta_time)`, `render(self)`.

### 3. Adaptation du `main.py`
-   **Fichier à modifier :** `main.py`
-   **Détails d'implémentation :**
    -   Le rôle de `main.py` est réduit. Il doit maintenant :
        1.  Initialiser Pygame.
        2.  Créer une instance du `GameStateManager`.
        3.  Créer une instance de l'état initial (ce sera le `MenuState`).
        4.  Pousser cet état initial dans le manager.
        5.  La boucle principale du jeu appellera désormais `manager.update()` et `manager.render()`.

---

## Phase 1 : Interface Utilisateur - Le Menu Principal

**Objectif :** Créer un point d'entrée professionnel pour le jeu et permettre au joueur de commencer une partie ou de quitter.

### 1. Création de l'État du Menu
-   **Fichier à créer :** `states/menu_state.py`
-   **Détails d'implémentation :**
    -   Créer une classe `MenuState` qui hérite de `BaseState`.
    -   `__init__()`: Initialiser les boutons ("Nouvelle Partie", "Charger", "Sauvegarder", "Quitter").
    -   `update()`: Gérer les entrées de la souris pour détecter le survol et le clic des boutons.
        -   Clic sur "Nouvelle Partie" -> `self.manager.switch_state(OverworldState())`.
        -   Clic sur "Quitter" -> `pygame.quit()`, `sys.exit()`.
        -   "Charger" / "Sauvegarder" : Pour l'instant, ces boutons seront désactivés ou afficheront un message "Fonctionnalité à venir".
    -   `render()`: Afficher une image de fond et dessiner les boutons.

### 2. Encapsulation du Jeu 3D Existant
-   **Fichier à créer :** `states/interior_state.py`
-   **Détails d'implémentation :**
    -   Créer une classe `InteriorState` qui hérite de `BaseState`.
    -   `__init__()`:
        -   Prendra en paramètre le chemin de la carte à charger (`map_path`).
        -   **C'est ici que l'on réutilise l'existant :** la méthode va créer une instance de votre classe `GameEngine` actuelle. `self.game_engine = GameEngine(screen, map_path)`.
    -   `update()`: Appellera simplement `self.game_engine.update(delta_time)`.
    -   `render()`: Appellera simplement `self.game_engine.render()`.
    -   **Test :** Temporairement, faites en sorte que le bouton "Nouvelle Partie" du menu lance un `InteriorState` avec une carte par défaut pour vérifier que votre jeu 3D fonctionne toujours à travers ce nouveau système.

---

## Phase 2 : Le Monde Extérieur (Overworld)

**Objectif :** Développer le mode de jeu en 2D vue de dessus.

### 1. Création de l'État du Monde Extérieur
-   **Fichier à créer :** `states/overworld_state.py`
-   **Détails d'implémentation :**
    -   Créer une classe `OverworldState` qui hérite de `BaseState`.
    -   `__init__()`: Chargera une carte spécifique au monde 2D.
    -   `update()`: Gérera la logique de déplacement du joueur en 2D et les interactions.
    -   `render()`: Fera appel à un nouveau moteur de rendu 2D.

### 2. Création du Moteur de Rendu 2D
-   **Fichier à créer :** `engine/renderer_2d.py`
-   **Détails d'implémentation :**
    -   Ce sera une classe `Renderer2D` beaucoup plus simple que le renderer 3D.
    -   Elle utilisera principalement `pygame.draw` et `screen.blit`.
    -   Méthodes à créer :
        -   `draw_map(map_data)`: Dessine le sol et les obstacles à partir d'un tileset.
        -   `draw_sprite(sprite, position)`: Dessine le joueur, les PNJ, etc.
        -   Gérera une caméra 2D qui suit le joueur.

### 3. Adaptation de l'Objet `Player`
-   **Fichier à modifier :** `objects/player.py`
-   **Détails d'implémentation :**
    -   La classe `Player` devra gérer un état interne (`self.mode = "3D"` ou `"2D"`).
    -   La méthode `update` devra avoir une branche : `if self.mode == "3D": ... else: ...`.
    -   La logique de mouvement 2D sera plus simple (4 ou 8 directions).

---

## Phase 3 : Transitions et Persistance des Données

**Objectif :** Permettre au joueur de passer de la 2D à la 3D de manière fluide, en conservant ses données.

### 1. Création d'un Objet de Session
-   **Fichier à créer :** `gameplay/game_session.py` (ou directement dans le `GameStateManager`)
-   **Détails d'implémentation :**
    -   Créer une classe `GameSession` (ou un simple dictionnaire) qui stockera toutes les données persistantes du joueur :
        -   Santé, inventaire, munitions (`ammo_pool`).
        -   Quêtes actives.
        -   Position du joueur dans le monde 2D.
    -   Cette instance sera créée au début d'une "Nouvelle Partie" et passée en paramètre à chaque nouvel état.

### 2. Implémentation des Points de Transition
-   **Fichier à modifier :** `world/map.py` et les fichiers `.json` des cartes.
-   **Détails d'implémentation :**
    -   Ajouter une nouvelle section dans les JSON des cartes 2D : `"transitions": [{"x": 10, "y": 15, "target_map": "...", "target_state": "InteriorState"}]`.
    -   Dans `OverworldState.update()`, vérifier si le joueur se trouve sur une tuile de transition.
    -   Si oui, appeler `self.manager.switch_state(InteriorState(map_path=..., session=...))`.
    -   Faire la même chose pour sortir d'un intérieur et revenir au monde 2D.

### 3. Sauvegarde et Chargement
-   **Fichiers à modifier :** `GameStateManager` et `MenuState`.
-   **Détails d'implémentation :**
    -   Créer des méthodes `save_game()` et `load_game()` dans le `GameStateManager`.
    -   Elles utiliseront les modules `pickle` ou `json` pour sérialiser l'objet `GameSession` dans un fichier.
    -   Activer les boutons "Sauvegarder" et "Charger" dans le menu pour appeler ces méthodes.

---

## Phase 4 : Systèmes de Gameplay Avancés

**Objectif :** Donner de la profondeur au jeu avec des quêtes et des dialogues dynamiques.

### 1. Gestionnaire de Quêtes
-   **Fichier à créer :** `gameplay/quest_manager.py`
-   **Détails d'implémentation :**
    -   Créer une classe `QuestManager`.
    -   Une instance sera stockée dans l'objet `GameSession`.
    -   Une quête sera un objet avec un `id`, un `titre`, une `description`, et une liste d'objectifs (triggers).
    -   Un **trigger** sera un dictionnaire : `{"type": "collect", "target": "item_id_123", "is_complete": false}` ou `{"type": "kill", "target": "monster_boss", "is_complete": false}`.
    -   Créer une méthode `notify(event_type, target_id)` (ex: `notify("collect", "item_id_123")`).
    -   Cette méthode sera appelée depuis le code du jeu (ex: dans `player.pickup_item`). Elle vérifiera si l'événement correspond à un objectif de quête active.

### 2. Gestionnaire de Dialogue
-   **Fichier à créer :** `gameplay/dialogue_manager.py`
-   **Détails d'implémentation :**
    -   Créer une classe `DialogueManager`.
    -   Quand le joueur interagit avec un PNJ, un `DialogueState` sera poussé sur la pile du `GameStateManager`.
    -   Cet état affichera une interface de dialogue (portrait du PNJ, texte, options de réponse).
    -   **Intégration d'Ollama :**
        -   Le `DialogueManager` aura une méthode `get_ollama_response(prompt)`.
        -   Cette méthode utilisera la librairie `requests` pour faire un appel POST à l'API locale d'Ollama (`http://localhost:11434/api/generate`).
        -   **Important :** L'appel étant potentiellement lent, il faudra afficher un indicateur de chargement ("...") dans l'interface de dialogue pendant que le jeu attend la réponse de l'IA.
        -   Le prompt envoyé à Ollama inclura le contexte de la conversation, les quêtes actuelles du joueur, et la personnalité du PNJ pour des réponses plus cohérentes.