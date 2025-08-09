

# Cahier des Charges - Projet Doom-Like

## Plan : Architecture Modulaire et Évolutive

### Structure des Dossiers

```plaintext
doom_like_project/
├── main.py
├── config.py
├── engine/
│   ├── ...
│   ├── game_engine.py
│   ├── renderer.py
│   └── input_manager.py
├── world/
│   ├── ...
│   ├── map.py
│   └── level_generator.py
├── objects/
│   ├── ...
│   ├── game_object.py
│   ├── player.py
│   ├── pnj.py
│   ├── friend.py
│   ├── foe.py
│   ├── weapon.py  <-- Rôle étendu
│   └── item.py
├── ai/
│   └── ...
└── assets/
    └── ...
```

### Description des Modules et Fichiers

- **main.py**
   Point d’entrée de l’application. Ce fichier initialise la fenêtre graphique (via Pygame, par exemple), charge la configuration, instancie le moteur de jeu et lance la boucle principale.
   *Responsabilités* : Initialisation, gestion des exceptions globales, démarrage de la boucle de jeu.
- **config.py**
   Définition des constantes et paramètres globaux (dimensions de la fenêtre, vitesse de déplacement, paramètres de caméra, etc.).
   *Responsabilités* : Centralisation de la configuration pour faciliter la maintenance et les réglages ultérieurs.
- **engine/game_engine.py**
   Contient la classe `GameEngine` qui orchestre le cycle de vie du jeu. Cette classe intègre le chargement des ressources, la mise à jour des états (physique, IA, entrées) et appelle le renderer à chaque frame.
   *Responsabilités* : Gestion de la boucle principale, synchronisation, appels aux mises à jour et au rendu.
- **engine/renderer.py**
  Module dédié au rendu 3D utilisant OpenGL. Il est responsable de :
  - La configuration de la perspective et de la caméra.
  - La création des shaders et la gestion des buffers.
  - La conversion de la carte 2D en géométrie 3D (par exemple, création de plans pour le sol et murs, génération de la profondeur).
  - Le rendu des sprites en billboarding pour que les personnages et items soient toujours orientés vers le joueur.
     *Technologies* : PyOpenGL, éventuellement combiné avec Pygame ou pyglet pour la gestion de la fenêtre.
- **engine/input_manager.py**
   Module gérant les entrées. Il traduit les événements clavier (z pour avancer, q pour strafe gauche, s pour reculer, d pour strafe droite) et souris (orientation de la vue).
   *Responsabilités* : Abstraction et normalisation des commandes, déclenchement d’événements dans le moteur.
- **world/map.py**
   Gère la représentation et la manipulation de la carte. À partir d’un array 2D (où 0.x désigne le sol et un entier plus élevé une texture de mur spécifique), le module génère la géométrie nécessaire à la construction du niveau.
   *Responsabilités* : Lecture des données, gestion de l’espace du jeu, placement statique des éléments.
- **world/level_generator.py**
   Si vous souhaitez une génération procédurale ou dynamique, ce module pourra fournir des fonctions pour créer ou modifier la carte en temps réel.
   *Responsabilités* : Création de niveaux, gestion des aléas dans la conception des niveaux.
- **objects/game_object.py**
   Définit une classe de base pour tous les objets du jeu (joueur, ennemis, items). On y trouve des attributs communs (position, rotation, méthode `update()` et `draw()`).
   *Responsabilités* : Normaliser le comportement et faciliter l’extension des objets du jeu.
- **objects/player.py**
   Classe spécifique dérivée de `GameObject` qui gère les statistiques du joueur (niveau, aptitudes, vie, etc.), son input particulier et ses interactions avec l’environnement et l’interface utilisateur.
   *Responsabilités* : Traitement des mouvements, gestion de l’expérience et évolution.
- ##### **objects/pnj.py**

   Classe de base pour les personnages non-joueurs (PNJ). Responsable de la lecture d'une configuration JSON externe pour définir les caractéristiques (santé, intelligence, mode de comportement) et le sprite associé. Elle peut être étendue pour des comportements spécifiques.

   **Responsabilités** : Initialisation d'un personnage neutre, affichage et réaction aux dégâts.
- ##### **objects/friend.py**

   Extension de `PNJ` pour les personnages amicaux ou neutres. Peut interagir avec le joueur via un système de dialogue ou changer de mode (allié, hostile).

   **Responsabilités** : Interaction pacifique, soutien en combat si en mode allié.

- ##### **objects/foe.py**

   Extension de `PNJ` pour les ennemis hostiles. Utilise le module `behavior.py` pour déterminer ses actions selon une IA basique (idle, patrol, chase, attack).

   **Responsabilités** : Suivi du joueur, attaque, déplacement dans la carte, animation selon l'état.

- ##### **objects/weapon.py**

   Classe représentant une arme utilisable par le joueur (et potentiellement les PNJ). Comporte le nom, le type (mêalée, distance...), l'état visuel (idle, attaque) et les propriétés d'attaque.

   **Responsabilités** : Définir la portée et la puissance, déclencher les actions lors d'une attaque, afficher l'arme dans le HUD.

- **objects/item.py**
   Classes pour les objets du jeu (armes, potions, objets interactifs). Ils sont rendus en mode sprite et doivent répondre à des événements de ramassage ou d’utilisation.
   *Responsabilités* : Gestion de l’interaction, déclenchement d’effets et modifications d’état du joueur.
- **ai/behavior.py**
   Module regroupant la logique décisionnelle des personnages non‑joueurs. Chaque ennemi peut par exemple choisir d’attaquer, se déplacer ou communiquer en fonction de son état et de l’environnement.
   *Responsabilités* : Implémentation d’un système d’états simples (machine à états) pour l’IA.
- **assets/**
   Dossier contenant toutes les ressources externes (textures, sprites, sons). Un système de chargement de ressources pourra être intégré dans un module supplémentaire ou dans `config.py` pour centraliser les chemins d’accès aux fichiers.
   *Responsabilités* : Stockage et accès aux ressources multimédias, permettant une séparation claire entre code et données.

### Moteur de Rendu et Technologies

1. **Utilisation d’OpenGL via PyOpenGL**
    Pour garantir un rendu 3D authentique (et non un effet 2.5D), le module `renderer.py` se chargera de :
   - Configurer une matrice de projection et une matrice vue pour simuler une caméra en mouvement.
   - Convertir les données d’une carte 2D en surfaces 3D, avec des textures adaptées.
   - Gérer les sprites des personnages et items en utilisant le billboarding pour qu’ils soient toujours orientés vers la caméra. La combinaison de PyOpenGL avec Pygame (ou pyglet) permet de gérer à la fois le rendu graphique et les événements d’entrée.
2. **Gestion des Entrées et de la Physique**
    Le module `input_manager.py` traitera les commandes utilisateur pour mettre à jour la position de la caméra et du joueur dans l’espace 3D, tandis que `game_engine.py` orchestrera la logique de déplacement et les interactions physiques entre objets.
3. **Programmation en Mode Objet**
    Chaque composant (carte, objets, joueur, ennemis, items) est conçu comme un objet autonome. Ceci facilite la maintenance et l’évolution du code, permettant par exemple l’ajout futur de nouvelles classes d’ennemis, de comportements spécifiques ou de niveaux plus complexes.
4. **Scalabilité et Maintenabilité**
   - **Modularité** : Chaque module ou dossier regroupe des responsabilités spécifiques, simplifiant ainsi l’extension et le débogage.
   - **Réutilisabilité** : L’utilisation d’une classe de base pour les objets et l’implémentation d’un système d’IA modulaire permettent d’introduire de nouveaux comportements sans modifier le noyau du moteur.
   - **Séparation des Ressources** : L’isolation du code de l’interface graphique des ressources (via le dossier assets et un module de chargement) garantit une meilleure gestion des modifications futures.