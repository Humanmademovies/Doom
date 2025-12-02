### Cahier des Charges - Projet Doom-Like (Mise à Jour)



Le projet a évolué d'un jeu "Doom-like" monolithique à une architecture modulaire et flexible. La vision finale est un jeu hybride qui combine une exploration en vue de dessus (Overworld 2D) avec des niveaux intérieurs en 3D (style FPS). Cette nouvelle structure permet la gestion de quêtes, de dialogues avancés, et la persistance des données du joueur à travers différentes phases de jeu. Le projet repose sur une machine à états pour orchestrer les transitions entre ces différents modes.

------



### Diagramme Hiérarchique du Projet (État Final)



Plaintext

```
doom_gemini_edition/
├── main.py
│   └── main()
├── game_state_manager.py (Implémenté, À modifier)
│   ├── GameStateManager
│   │   ├── push_state()
│   │   ├── pop_state()
│   │   ├── switch_state()
│   │   ├── get_active_state()
│   │   ├── update()
│   │   ├── render()
│   │   ├── save_game()
│   │   └── load_game()
├── config.py (Implémenté)
│   └── WEAPON_CONFIG
├── states/
│   ├── base_state.py (Implémenté)
│   │   └── BaseState
│   │       ├── update()
│   │       └── render()
│   ├── menu_state.py (Implémenté)
│   │   └── MenuState
│   │       └── start_new_game()
│   ├── map_selection_state.py (Implémenté)
│   │   └── MapSelectionState
│   │       └── start_game_with_map()
│   ├── interior_state.py (Implémenté, À modifier)
│   │   └── InteriorState
│   ├── pause_state.py (Implémenté)
│   │   └── PauseState
│   │       ├── resume_game()
│   │       ├── save_game()
│   │       └── load_game()
│   ├── game_over_state.py (Implémenté)
│   │   └── GameOverState
│   │       └── restart_level()
│   └── overworld_state.py (À faire)
│       └── OverworldState
│           ├── __init__()
│           ├── update()
│           └── render()
├── engine/
│   ├── __init__.py (Implémenté)
│   ├── game_engine.py (Implémenté)
│   │   └── GameEngine
│   │       ├── update()
│   │       └── render()
│   ├── renderer.py (Implémenté)
│   │   └── Renderer
│   │       ├── render_hud()
│   │       ├── _render_ammo_info()
│   │       └── render_weapon_hud()
│   ├── renderer_2d.py (À faire)
│   │   └── Renderer2D
│   │       ├── draw_map()
│   │       ├── draw_sprite()
│   │       └── update_camera()
│   └── input_manager.py (Implémenté)
│       └── InputManager
│           ├── update()
│           ├── is_mouse_held()
│           └── is_key_just_pressed()
├── world/
│   ├── __init__.py (Implémenté)
│   ├── map.py (Implémenté, À modifier)
│   │   └── GameMap
│   │       ├── load_from_file()
│   │       └── (Nouvel attribut: transitions)
│   └── level_generator.py (Implémenté)
│       └── LevelGenerator
├── objects/
│   ├── __init__.py (Implémenté)
│   ├── game_object.py (Implémenté)
│   │   └── GameObject
│   ├── player.py (Implémenté, À modifier)
│   │   └── Player
│   │       ├── fire()
│   │       ├── reload_weapon()
│   │       ├── pickup_weapon()
│   │       ├── add_ammo()
│   │       └── (Nouvel attribut: self.mode)
│   ├── pnj.py (Implémenté)
│   │   └── PNJ
│   │       └── take_damage()
│   ├── friend.py (Implémenté)
│   │   └── Friend
│   ├── foe.py (Implémenté)
│   │   └── Foe
│   │       └── update()
│   ├── weapon.py (Implémenté, À modifier)
│   │   └── Weapon
│   │       ├── perform_attack()
│   │       └── reload()
│   └── item.py (Implémenté)
│       └── Item
│           └── on_pickup()
├── gameplay/
│   ├── serialization.py (Implémenté)
│   │   ├── serialize_object()
│   │   └── deserialize_object()
│   ├── game_session.py (À faire)
│   │   └── GameSession
│   ├── quest_manager.py (À faire)
│   │   └── QuestManager
│   └── dialogue_manager.py (À faire)
│       └── DialogueManager
├── ai/
│   └── behavior.py (Implémenté)
│       └── decide_action()
└── assets/
    ├── maps/
    └── ...
```

------



### Description des Modules et Fichiers





#### 1. `main.py`



- **Statut :** (Implémenté)
- **Description :** Point d'entrée de l'application. Initialise Pygame et le `GameStateManager`, puis lance la boucle principale du jeu. Son rôle est minimal, déléguant la logique de jeu aux états.



#### 2. `game_state_manager.py`



- **Statut :** (Implémenté, À modifier)
- **Description :** C'est le chef d'orchestre du jeu. Il gère la pile d'états et assure la transition entre eux. Les fonctions `save_game()` et `load_game()` sont présentes et fonctionnent.
- **À modifier :** Il devra gérer une instance de `GameSession` pour la persistance des données entre les états de jeu.



#### 3. `config.py`



- **Statut :** (Implémenté)
- **Description :** Centralise les paramètres du jeu, tels que les dimensions de l'écran, la vitesse du joueur, et la configuration des armes via le dictionnaire `WEAPON_CONFIG`.



#### 4. `states/`



- **Statut :** (Implémenté, À faire)
- **Description :** Ce dossier contient les classes d'état de jeu, toutes dérivées de `BaseState`.
  - `base_state.py` : Classe de base abstraite. (Implémenté)
  - `menu_state.py` : Gère le menu principal et permet de passer à l'écran de sélection de carte. (Implémenté)
  - `map_selection_state.py` : Permet au joueur de choisir une carte. (Implémenté)
  - `interior_state.py` : Encapsule le moteur de jeu 3D et gère les transitions vers la pause ou l'écran de fin de partie. (Implémenté)
  - `pause_state.py` : Gère le menu de pause et offre des options de sauvegarde et de chargement. (Implémenté)
  - `game_over_state.py` : Gère l'écran de fin de partie. (Implémenté)
  - `overworld_state.py` : Gérera le gameplay en vue de dessus, les déplacements en 2D et les interactions avec les points de transition. (À faire)



#### 5. `engine/`



- **Statut :** (Implémenté, À faire)
- **Description :** Contient les composants clés du moteur.
  - `game_engine.py` : Le cœur de l'état `InteriorState`. Gère la boucle de jeu, les mises à jour des entités et la logique de tir. (Implémenté)
  - `renderer.py` : Gère le rendu 3D avec OpenGL, le HUD (barre de vie, mini-carte, informations sur les munitions) et les sprites. (Implémenté)
  - `renderer_2d.py` : Gérera le rendu spécifique au mode "Overworld". (À faire)
  - `input_manager.py` : Gère les entrées clavier et souris. (Implémenté)



#### 6. `world/`



- **Statut :** (Implémenté, À modifier)
- **Description :** Gère les niveaux.
  - `map.py` : Lit et interprète les fichiers JSON des cartes pour construire l'environnement de jeu. (Implémenté)
  - `map.py` : Le format JSON des cartes devra être mis à jour pour inclure des points de transition entre les cartes 2D et 3D. (À modifier)
  - `level_generator.py` : Contient la logique pour la génération procédurale de labyrinthes. (Implémenté, mais non intégré au jeu principal)



#### 7. `objects/`



- **Statut :** (Implémenté, À modifier)
- **Description :** Contient la hiérarchie des objets du jeu.
  - `game_object.py` : Classe de base pour toutes les entités. (Implémenté)
  - `player.py` : Représente le joueur, ses statistiques, son inventaire d'armes et d'objets, et son pool de munitions. (Implémenté)
  - `player.py` : La classe devra gérer un état interne pour son mode de jeu (`2D` ou `3D`). (À modifier)
  - `weapon.py` : Définit le comportement et les statistiques d'une arme. (Implémenté)
  - `weapon.py` : La fonctionnalité de changement de mode de tir (`"semi"`, `"auto"`) n'est pas encore implémentée. (À faire)
  - `item.py` : Représente un objet ramassable. Sa logique est un aiguillage intelligent vers les méthodes du joueur. (Implémenté)
  - `pnj.py` : Classe de base pour les PNJ. (Implémenté)
  - `friend.py` : PNJ non-hostile, avec un comportement de dialogue basique. (Implémenté)
  - `foe.py` : PNJ hostile, utilisant l'IA pour patrouiller, poursuivre et attaquer. (Implémenté)



#### 8. `gameplay/`



- **Statut :** (Implémenté, À faire)
- **Description :** Ce dossier est destiné à la logique de jeu avancée.
  - `serialization.py` : Contient les fonctions de sérialisation et de désérialisation des objets. (Implémenté)
  - `game_session.py` : Contiendrait toutes les données persistantes du joueur (santé, inventaire, quêtes) pour les transitions entre les états. (À faire)
  - `quest_manager.py` : Gèrera le système de quêtes. (À faire)
  - `dialogue_manager.py` : Gèrera les interactions de dialogue avec les PNJ. (À faire)



#### 9. `ai/`



- **Statut :** (Implémenté)
- **Description :** Module qui contient la logique décisionnelle simple des PNJ.
  - `behavior.py` : Contient la fonction `decide_action()` qui détermine l'action d'un PNJ en fonction de la distance avec le joueur. (Implémenté)