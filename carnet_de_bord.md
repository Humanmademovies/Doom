- ## Feuille de Route Technique - Projet "Doom Gemini"

  ### **ÉTAT D'AVANCEMENT : PHASE 3 TERMINÉE**

  Le moteur de jeu est désormais **stable et persistant**.
  Les données du joueur (Santé, Inventaire, Munitions) et l'état du monde (Ennemis tués, Objets ramassés) sont conservés entre les transitions de niveaux (2D <-> 3D) et via le système de Sauvegarde/Chargement.

  ---

  ### **HISTORIQUE DES PHASES**

  #### ✅ Phase 0 à 2 : Fondations, Moteur 3D, Overworld 2D
  - Moteur Raycasting/OpenGL fonctionnel.
  - Système de déplacement 2D et 3D opérationnel.
  - Masques de collision bâtiments et transitions de cartes.

  #### ✅ Phase 3 : Cœur du Moteur & Persistance (COMPLÉTÉ)
  - **Session de Jeu (`GameSession`) :** Implémentée. Elle agit comme source unique de vérité.
  - **Sauvegarde/Chargement :** Fonctionnel sur n'importe quelle carte. Utilise la sérialisation JSON de la session.
  - **Continuité 2D/3D :** Le joueur conserve ses stats et revient à la position exacte devant la porte dans l'Overworld.
  - **Persistance du Monde :**
    - Les items ramassés ne réapparaissent plus.
    - Les ennemis tués réapparaissent en tant que cadavres (état `dead`).
    - IDs uniques générés de manière déterministe pour chaque entité.

  ---

  ### **PHASE ACTUELLE : Phase 4 - Vie et Narration**

  **Objectif :** Transformer ce monde persistant mais silencieux en un univers interactif.

  #### **1. Système de Dialogues (PRIORITAIRE)**
  - **Structure :** Créer `gameplay/dialogue_manager.py`.
  - **Interface :** Créer un `DialogueState` (fenêtre modale par-dessus le jeu).
  - **Interaction :** Modifier `Friend` pour déclencher le dialogue avec la touche 'E'.
  - **Contenu :** Intégration de fichiers JSON de dialogues ou connecteur IA (Ollama) ultérieur.

  #### **2. Système de Quêtes**
  - **Structure :** Créer `gameplay/quest_manager.py` (intégré à la `GameSession`).
  - **Logique :** Définir des "Triggers" (ex: Ramasser Objet X -> Valider Étape Y).
  - **UI :** Afficher les objectifs en cours.

  ---

  ### **Backlog (Améliorations futures)**

  - **Gameplay :** Sélecteur de tir (Semi/Auto) pour les armes.
  - **Inventaire :** Limite d'armes et système de "drop" au sol.
  - **IA :** Comportements plus complexes (couverture, fuite).