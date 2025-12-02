# Cahier des Charges Technique - Projet Doom Gemini

## 1. Vision du Projet

Le projet est un jeu hybride combinant une exploration en vue de dessus (Overworld 2D) et des phases d'action/exploration en vue subjective (FPS 3D type "Doom-like"). Le jeu repose sur une architecture modulaire stricte, pilotée par une **Session de Jeu** centrale qui assure la persistance des données et la continuité de l'expérience entre les différents modes de vue et les sauvegardes.

## 2. Architecture du Projet

Le projet est structuré autour d'un gestionnaire d'états et d'une session de données persistante.

### Arborescence des Fichiers

Plaintext

```
doom_gemini_edition/
├── main.py                     # Point d'entrée : Initialisation Pygame & Manager
├── game_state_manager.py       # Chef d'orchestre : Gère la pile d'états et la GameSession
├── config.py                   # Configuration globale (Constantes, résolutions)
├── lancer_jeu.sh               # Script de lancement (Environnement Conda)
│
├── states/                     # Les différents écrans/modes de jeu
│   ├── base_state.py           # Classe abstraite parente
│   ├── menu_state.py           # Menu Principal (Nouvelle Partie / Charger / Quitter)
│   ├── map_selection_state.py  # Outil de debug pour tester des cartes spécifiques
│   ├── interior_state.py       # Conteneur du mode FPS 3D
│   ├── overworld_state.py      # Conteneur du mode Exploration 2D
│   ├── pause_state.py          # Menu de Pause (Reprendre / Sauvegarder / Charger / Quitter)
│   └── game_over_state.py      # Écran de fin de partie
│
├── engine/                     # Moteur technique
│   ├── game_engine.py          # Cœur logique 3D : Boucle de jeu, Raycasting (Interaction E), Events
│   ├── renderer.py             # Moteur de rendu 3D (OpenGL/Raycasting) & HUD
│   ├── renderer_2d.py          # Moteur de rendu 2D (Tilemap & Sprites)
│   └── input_manager.py        # Gestion des entrées (Clavier/Souris)
│
├── world/                      # Gestion des niveaux
│   ├── map.py                  # Chargeur de cartes JSON, Générateur d'IDs, Filtre de persistance
│   ├── level_generator.py      # Générateur procédural (Labyrinthes)
│   └── sprite_analyzer.py      # Analyse d'images pour détection de portes/logos
│
├── objects/                    # Entités du jeu
│   ├── game_object.py          # Classe de base
│   ├── player.py               # Avatar du joueur (Stats, Inventaire, Logique de tir)
│   ├── pnj.py                  # Classe de base des PNJ (ID unique, Santé, États)
│   ├── friend.py               # PNJ Amical (Interaction dialogue)
│   ├── foe.py                  # PNJ Hostile (IA, Combat)
│   ├── item.py                 # Objets ramassables (Potions, Munitions, Armes)
│   └── weapon.py               # Logique des armes (Tir, Rechargement)
│
├── gameplay/                   # Logique de jeu transverse (Le "Cerveau")
│   ├── game_session.py         # Stockage persistant (Inv, Stats, World State)
│   ├── serialization.py        # Outils de sérialisation JSON pour Sauvegarde/Chargement
│   ├── dialogue_manager.py     # (PRÉVU - Phase 4) Gestion des dialogues
│   └── quest_manager.py        # (PRÉVU - Phase 4) Gestion des quêtes
│
├── ai/                         # Intelligence Artificielle
│   └── behavior.py             # Arbre de comportement simple pour les ennemis
│
└── assets/                     # Ressources
    ├── maps/                   # Fichiers JSON des niveaux (Intérieurs et Extérieurs)
    ├── textures/               # Textures des murs/sols
    ├── sprites/                # Sprites des entités et bâtiments
    └── ui/                     # Éléments d'interface et polices
```

## 3. Description Fonctionnelle des Modules

### A. Noyau & Gestion (`root`)

- **`game_state_manager.py`** :
  - **Rôle :** Gère les transitions entre les écrans (Menu -> Jeu -> Pause).
  - **Responsabilité critique :** Possède l'instance unique de `GameSession`.
  - **Fonctions :** `start_new_session()`, `save_game()`, `load_game()`.
- **`main.py`** : Initialise Pygame et lance la boucle principale du Manager.

### B. Persistance & Données (`gameplay`)

- **`game_session.py`** : **Le Cerveau**.
  - Stocke l'état complet du joueur : PV, Munitions, Inventaire (Armes/Items).
  - Stocke l'état du monde (`world_state`) : Dictionnaire par carte listant les IDs des ennemis tués et objets ramassés.
  - Gère la position de retour dans l'Overworld lors des transitions.
  - Fournit les méthodes `to_dict()` et `load_from_dict()` pour la sauvegarde disque.
- **`serialization.py`** : Convertit les objets complexes (Player, Weapon, Item) en dictionnaires pour le JSON et inversement. Gère la robustesse (attributs manquants).

### C. États de Jeu (`states`)

- **`menu_state.py`** : Point d'entrée. Permet de lancer une "Nouvelle Partie" (crée une session vierge) ou de "Charger" une sauvegarde existante.
- **`overworld_state.py`** : Mode 2D.
  - Initialise le joueur avec les données de la `GameSession`.
  - Gère les déplacements sur la carte globale.
  - Détecte les collisions avec les portes des bâtiments.
  - **Avant transition :** Sauvegarde la position et les stats du joueur dans la Session.
- **`interior_state.py`** : Mode 3D.
  - Initialise le `GameEngine` en lui passant la `GameSession`.
  - Gère la boucle de gameplay FPS.
  - Gère le retour à l'Overworld sur signal `EXIT_TO_MAP`.

### D. Moteur & Logique (`engine`)

- **`game_engine.py`** :
  - Moteur de jeu 3D principal.
  - Gère la physique, les tirs et les mises à jour des entités.
  - **Interaction :** Gère le Raycasting pour détecter l'activation des portes (Touche 'E').
  - **Persistance Live :** Détecte la mort des ennemis et le ramassage des items pour les enregistrer immédiatement dans la `GameSession`.
- **`renderer.py`** : Moteur de rendu Raycasting/OpenGL pour la 3D et affichage du HUD (Vie, Munitions, Inventaire).
- **`renderer_2d.py`** : Moteur de rendu pour la vue de dessus (Tilemap, Sprites, Bâtiments).

### E. Monde & Niveaux (`world`)

- **`map.py`** :
  - Charge les fichiers `.json` de description des niveaux.
  - **Identité :** Génère des IDs uniques et déterministes pour chaque entité (basés sur leur position x,y).
  - **Filtrage :** Interroge la `GameSession` au chargement. Si un objet est marqué "collected", il n'est pas instancié. Si un ennemi est marqué "killed", il est instancié directement à l'état de cadavre.

### F. Objets Interactifs (`objects`)

- **`item.py`** : Possède un ID unique. Gère son ramassage et son effet.
- **`pnj.py` / `foe.py`** : Possèdent un ID unique. Gèrent leur état (vivant/mort), leur IA et leurs PV.

## 4. Fonctionnalités Clés Implémentées

1. **Hybridité 2D/3D :** Transition fluide entre l'Overworld (Exploration) et les Intérieurs (Combat).
2. **Persistance Totale :**
   - Le joueur garde ses acquis (XP, Items, PV) tout au long du jeu.
   - Le monde se "souvient" des actions du joueur (Monstres éliminés, Coffres ouverts).
3. **Sauvegarde Universelle :** Possibilité de sauvegarder et charger n'importe où (2D ou 3D), l'état exact est restauré.
4. **Interaction Environnementale :** Système de portes interactives (Touche 'E') avec Raycasting précis.

## 5. Prochaines Étapes (Phase 4)

- **Système de Dialogues :** Implémentation du `dialogue_manager.py` et de l'état `DialogueState` pour permettre des conversations avec les PNJ amicaux.
- **Système de Quêtes :** Création du `quest_manager.py` pour structurer la progression du joueur à travers des objectifs.