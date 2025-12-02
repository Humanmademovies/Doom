

Nous avons terminé avec succès toute la **Phase 2 : Le Monde Extérieur (Overworld)** ainsi qu'une partie de la **Phase 3** concernant les transitions. La base est maintenant très solide.

Voici la feuille de route mise à jour, qui se concentre sur les prochaines étapes logiques pour donner de la profondeur au jeu.

------



## Feuille de Route Technique (Mise à Jour - FOCUS PERSISTANCE)

**ÉTAT CRITIQUE :** La Phase 2 (Overworld) est fonctionnelle, mais la **Phase 3 est bloquée**. Les transitions entre la carte 2D et les niveaux 3D réinitialisent actuellement le joueur (perte d'inventaire, de PV, etc.) car aucune session globale n'existe.

### **PRIORITÉ ABSOLUE : Phase 3 - Persistance et Session (BLOQUANT)**

**Objectif :** Implémenter la `GameSession` pour stocker l'état du joueur indépendamment des niveaux. Sans cela, le jeu n'est qu'une suite de niveaux déconnectés.

- **[URGENT] Création de `gameplay/game_session.py`**
  - **Détails :** Classe conteneur (Singleton ou instance unique dans le Manager) qui stocke :
    - `player_stats` (PV, max_health)
    - `inventory` (items, armes, munitions)
    - `world_state` (carte actuelle, position d'entrée dans l'Overworld pour le retour)
    - `flags` (état des quêtes, dialogues déjà lus)

- **[URGENT] Refonte du `GameStateManager`**
  - **Détails :** Il doit initialiser la `GameSession` au démarrage (`MenuState` -> Nouvelle Partie) et la passer en argument à chaque nouvel état (`OverworldState`, `InteriorState`).

- **[URGENT] Connexion des États**
  - **Modifier `OverworldState` :** À l'initialisation, charger la position et l'état du joueur depuis la `GameSession`.
  - **Modifier `InteriorState` / `GameEngine` :** À l'initialisation, configurer le `Player` 3D avec les stats de la `GameSession`. En fin de niveau (ou transition), mettre à jour la `GameSession`.

- **Refonte de la Sauvegarde/Chargement**
  - **Détails :** Le système actuel (qui cherche dans `InteriorState`) est obsolète.
  - La sauvegarde doit maintenant sérialiser uniquement l'objet `GameSession`.

---

### Phase 4 : Systèmes de Gameplay Avancés (En attente de la Phase 3)

**Objectif :** Donner un but et de la vie au monde. Ne peut être commencé tant que la session n'existe pas.

#### 1. Gestionnaire de Quêtes
- **Fichier à créer :** `gameplay/quest_manager.py` (Intégré dans `GameSession`)

#### 2. Gestionnaire de Dialogue
- **Fichier à créer :** `gameplay/dialogue_manager.py`

---

### Améliorations "Quality of Life" (Backlog)

- **Armes :** Sélecteur de tir (Semi/Auto) dans `weapon.py`.
- **Inventaire :** Limite d'armes et drop au sol.