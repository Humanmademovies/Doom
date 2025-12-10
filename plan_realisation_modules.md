# Plan de Réalisation Technique - Mise à Jour (Phase 4)

Ce document détaille les étapes restantes pour finaliser les systèmes narratifs et affiner le gameplay.
Les Phases 0 à 3 (Moteur 3D, Overworld 2D, Persistance & Sauvegarde) sont terminées et fonctionnelles.

---

## Phase 4 : Systèmes de Narration et Quêtes

**Objectif :** Enrichir l'univers avec des interactions non-combatives et des objectifs suivis.

### 1. Gestionnaire de Quêtes

- **Fichier à créer :** `gameplay/quest_manager.py`
- **Détails d'implémentation :**
  - Créer une classe `QuestManager`.
  - Intégrer une instance de ce manager dans la `GameSession`.
  - Définir une structure de données `Quest` contenant :
    - Métadonnées : `id`, `titre`, `description`.
    - État : `status` (active, completed, failed).
    - Objectifs : Liste de triggers (ex: `{"type": "kill", "target": "monster_ID", "count": 5, "current": 0}`).
  - Implémenter la méthode `notify(event_type, target_id)` :
    - Cette méthode sera appelée par le `GameEngine` lors d'événements clés (mort d'un ennemi, ramassage d'item).
    - Elle vérifiera si l'événement fait progresser une quête active.

### 2. Gestionnaire de Dialogue & IA

- **Fichier à créer :** `gameplay/dialogue_manager.py`
- **Détails d'implémentation :**
  - Créer une classe `DialogueManager`.
  - Créer un nouvel état `DialogueState` (UI superposée au jeu) pour afficher les échanges sans arrêter le moteur, mais en bloquant les inputs de mouvement.
  - **Intégration Ollama (IA Locale) :**
    - Utiliser la librairie `requests` pour appeler l'API locale d'Ollama (`POST /api/generate`).
    - Gérer l'attente de réponse (afficher "..." ou une animation de pensée).
    - Construire des prompts dynamiques (Context Injection) incluant :
      - L'état de santé du joueur.
      - Les quêtes en cours.
      - La personnalité du PNJ (définie dans son fichier de config).

---

## Améliorations Gameplay (Polissage)

### 1. Modes de Tir des Armes

- **Fichiers concernés :** `objects/weapon.py`, `objects/player.py`, `engine/input_manager.py`.
- **Détails :**
  - Ajouter un attribut `fire_mode` ("semi", "auto") à la classe `Weapon`.
  - Ajouter une méthode `switch_fire_mode()` (touche 'V' ou clic molette).
  - Modifier `InputManager` pour distinguer clairement :
    - `is_mouse_just_pressed()` (pour le semi-auto).
    - `is_mouse_held()` (pour l'automatique).

### 2. Gestion d'Inventaire Avancée

- **Fichiers concernés :** `objects/player.py`, `objects/item.py`.
- **Détails :**
  - Implémenter une limite d'inventaire (ex: 2 armes principales max).
  - Implémenter le système de "Drop" :
    - Si l'inventaire est plein lors d'un ramassage, l'arme active est retirée de l'inventaire.
    - Une nouvelle instance de `Item` (type arme) est créée au sol à la position du joueur pour représenter l'arme lâchée.

------

### 📅 Phase 1 : Architecture des Données & Persistance

**Objectif :** Rendre les PNJ "intelligents" au niveau des données avant même de brancher l'IA.

- **1.1. Refonte du Schéma de Données PNJ (`config.json`)**
  - Définition du nouveau standard JSON incluant :
    - `identity` : Nom, Backstory, Intentions (Long Terme).
    - `stats` : P, S, I (déjà existant, à conserver).
    - `psychology` : Big Five (0.0 à 1.0), Traits spécifiques.
    - `assets` : Mapping des fichiers sprites par émotion/intensité.
  - *Fichiers à modifier :* `assets/pnj/[nom]/config.json`.
- **1.2. Extension de la Classe `PNJ` et `Friend`**
  - Ajout des attributs dynamiques (non stockés dans le JSON statique mais instanciés) :
    - `current_emotion` (Enum: Neutral, Joy, Fear, Anger, Sadness, Disgust, Surprise).
    - `emotion_intensity` (Enum: Low, Medium, High).
    - `trust_level` (float 0-100).
    - `short_term_intent` (String dynamique).
    - `alignment` (Friend/Foe).
  - Mise à jour du constructeur pour charger ces nouvelles données.
  - *Fichiers à modifier :* `objects/pnj.py`, `objects/friend.py`.
- **1.3. Mise à jour de la `GameSession` (Sauvegarde)**
  - Assurer que l'état psychologique (Confiance, Émotion, Alignement) est sérialisé dans `savegame.json` pour que le PNJ ne "reboot" pas ses sentiments au rechargement.
  - *Fichiers à modifier :* `gameplay/game_session.py`, `gameplay/serialization.py`.

------

### 🧠 Phase 2 : Le "Cerveau" (Backend Logic & IA)

**Objectif :** Créer le moteur décisionnel asynchrone (Director/Actor).

- **2.1. Infrastructure Threading (`DialogueManager`)**
  - Création de la classe avec gestion de Files d'attente (`Queues`) : `input_queue`, `state_queue`, `text_stream_queue`.
  - Implémentation de la méthode `process_input(text)` qui lance le thread sans bloquer le jeu.
  - *Fichier à créer :* `gameplay/dialogue_manager.py`.
- **2.2. Implémentation du Pipeline "Director" (Évaluateur)**
  - Construction du Prompt Système "Director" : Injection des données PNJ (Backstory, Intentions, PSI, Big Five, Mémoire).
  - Définition du schéma de sortie JSON attendu (Emotion, Intensité, Confiance +/-, Event, Instruction Acteur).
  - Parsing robuste de la réponse JSON du LLM.
  - Application des changements d'état (ex: Passage de Friend à Foe si Confiance < Seuil).
- **2.3. Implémentation du Pipeline "Actor" (Générateur)**
  - Construction du Prompt Système "Actor" : Injection de l'Instruction du Director + Style de parole (basé sur PSI/Big Five).
  - Connexion à l'API Ollama (Stream mode).
  - Remplissage de la `text_stream_queue` caractère par caractère.
- **2.4. Système de Mémoire (RAG simplifié)**
  - **Court terme :** `deque(maxlen=10)` stocké dans l'instance PNJ.
  - **Long terme :** Sauvegarde des résumés de conversation dans un fichier JSON dédié (`history/[pnj_id].json`).
  - Injecter le contexte pertinent dans le prompt du Director.

------

### 👁️ Phase 3 : Interface & Rendu (Frontend)

**Objectif :** Afficher le résultat visuellement.

- **3.1. Création de l'État `DialogueState`**
  - Développement de l'Overlay (OpenGL surcouche 2D).
  - Gestion des Inputs (Saisie texte libre, Touche Entrée, Echap).
  - *Fichier à créer :* `states/dialogue_state.py`.
- **3.2. Système de Sprites Dynamiques**
  - Logique de chargement de texture : `get_sprite(emotion, intensity)`.
  - Fallback : Si `joy_high.png` n'existe pas, charger `joy_medium.png` ou `idle.png`.
  - Affichage du portrait à gauche/droite.
- **3.3. Affichage du Texte Streamé**
  - Lecture de la `text_stream_queue` à chaque frame.
  - Effet "machine à écrire" fluide.
  - Gestion du retour à la ligne automatique (Word wrapping).

------

### ⚙️ Phase 4 : Gameplay & Intégration PSI

**Objectif :** Que les stats aient un impact réel.

- **4.1. Câblage des Events**
  - Si le Director renvoie un event `GIVE_ITEM`, déclencher l'ajout à l'inventaire du joueur via `GameSession`.
  - Si le Director renvoie un event `ATTACK`, fermer le dialogue et passer le PNJ en mode `Foe` (Combat).
- **4.2. Influence PSI sur les Prompts**
  - **S (Sensibilité) élevée :** Le Director détecte mieux les mensonges du joueur. L'Acteur utilise un langage plus émotionnel/poétique.
  - **I (Intelligence) élevée :** Le Director analyse logiquement les incohérences. L'Acteur utilise un vocabulaire complexe.
  - **P (Puissance) élevée :** L'Acteur est plus direct, intimidant ou confiant.

------

### 🧪 Phase 5 : Tests & Calibration (Iterative)

**Objectif :** Équilibrer le comportement.

- **5.1. Mocking (Tests sans IA)**
  - Remplacer les appels Ollama par des fonctions simulant des réponses JSON et Texte pour valider l'UI et le Threading sans latence.
- **5.2. Prompt Engineering (Tuning)**
  - Ajuster les prompts systèmes pour que le Director ne soit ni trop permissif ni trop psychorigide.
  - Tester la cohérence des traits Big Five.

------

### Résumé des Nouveaux Fichiers / Modifications Majeures

1. `gameplay/dialogue_manager.py` (Cerveau)
2. `states/dialogue_state.py` (Visage)
3. `objects/friend.py` (Corps - mise à jour)
4. `assets/pnj/.../config.json` (Âme - refonte structurelle)

**Validé ?** Si oui, nous passerons à l'implémentation de la **Phase 1 (Données)**.