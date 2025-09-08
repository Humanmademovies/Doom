

Nous avons terminé avec succès toute la **Phase 2 : Le Monde Extérieur (Overworld)** ainsi qu'une partie de la **Phase 3** concernant les transitions. La base est maintenant très solide.

Voici la feuille de route mise à jour, qui se concentre sur les prochaines étapes logiques pour donner de la profondeur au jeu.

------



## Feuille de Route Technique (Mise à Jour)





### **Phase 3 : Persistance des Données du Joueur**



**Objectif :** Rendre l'expérience de jeu continue. Les informations du joueur (santé, inventaire, etc.) doivent être conservées lorsqu'il passe d'un intérieur (3D) à l'extérieur (2D), et vice-versa.

- **Fichier à créer :** `gameplay/game_session.py`
  - **Détails :** Créer une classe `GameSession` qui contiendra toutes les données persistantes :
    - `player_health`
    - `player_inventory_items`
    - `player_inventory_weapons`
    - `player_ammo_pool`
    - `active_quests` (pour la phase 4)
    - La position du joueur dans l'Overworld pour qu'il réapparaisse au bon endroit en sortant d'un bâtiment.
- **Fichier à modifier :** `game_state_manager.py`
  - **Détails :** Le manager devra posséder une instance de `GameSession`. Au lieu de créer des états "vides", il leur passera cette session pour qu'ils puissent s'initialiser avec les bonnes données.
- **Fichiers à modifier :** `states/overworld_state.py` et `states/interior_state.py`
  - **Détails :** Leurs constructeurs `__init__` devront accepter l'objet `GameSession` et l'utiliser pour configurer le joueur au lieu de le créer de zéro à chaque fois.

------



### **Phase 4 : Systèmes de Gameplay Avancés**



**Objectif :** Donner un but et de la vie au monde avec des quêtes et des dialogues.



#### **1. Gestionnaire de Quêtes**



- **Fichier à créer :** `gameplay/quest_manager.py`
  - **Détails :**
    - Créer une classe `QuestManager` qui sera stockée dans la `GameSession`.
    - Définir une structure de quête simple (un dictionnaire ou une classe) avec un `id`, un `titre`, une `description`, et une liste d'objectifs (par exemple : `{"type": "collect", "target_id": "key_office", "completed": false}`).
    - Le `QuestManager` aura une méthode `notify(event_type, event_data)` qui sera appelée depuis le code du jeu (par exemple, dans `player.py` quand un objet est ramassé) pour vérifier si un objectif de quête est rempli.



#### **2. Gestionnaire de Dialogue**



- **Fichier à créer :** `gameplay/dialogue_manager.py`
  - **Détails :**
    - Créer un `DialogueManager` de base. Dans un premier temps, il pourra simplement charger et afficher des dialogues prédéfinis depuis un fichier JSON.
    - Créer un nouvel état de jeu `DialogueState` qui se superposera à l'écran, affichant le texte et les options de réponse.
- **Fichier à modifier :** `objects/friend.py`
  - **Détails :** La méthode `update` devra détecter une touche d'interaction (par exemple 'E') lorsque le joueur est proche pour déclencher le `DialogueState`.

------



### **Améliorations de l'Existant (Qualité de vie)**



Ces points sont listés dans tes documents et peuvent être faits à tout moment.

- **Fichier à modifier :** `objects/weapon.py` et `engine/input_manager.py`
  - **Détails :** Ajouter un attribut `fire_mode` ("semi", "auto") aux armes et la logique pour basculer entre les modes. L'`InputManager` devra distinguer un clic simple (`is_mouse_clicked`) d'un clic maintenu (`is_mouse_held`).
- **Fichier à modifier :** `objects/player.py`
  - **Détails :**
    - Limiter l'inventaire d'armes (par exemple, à 4).
    - Si le joueur ramasse une arme alors que l'inventaire est plein, "lâcher" l'arme actuellement équipée à sa place.

Je suis prêt pour la prochaine instruction.