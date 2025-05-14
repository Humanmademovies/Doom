

------

### 1. ✅ `player.py`

**Fonction : `__init__`**

- Ajouter deux listes distinctes : `inventory_items`, `inventory_weapons`
- Ajouter deux index : `item_index`, `weapon_index`

**Fonctions :**

- `add_to_inventory(item)` → répartir l’objet dans la bonne liste
- `scroll_inventory(direction)` → à séparer en :
  - `scroll_items(direction)` pour les items
  - `scroll_weapons(direction)` pour les armes
- `get_selected_item()` → à séparer aussi
  - `get_selected_item()` (items)
  - `get_selected_weapon()` (armes)
- `use_selected_item()` → mise à jour pour utiliser `inventory_items[item_index]`
- `update()` → gérer les touches ↑ ↓ ← → correctement pour le scrolling (appel des nouvelles méthodes)

------

### 2. ✅ `input_manager.py`

**Fonction : `update()`**

- Remplacer gestion de `left_pressed` et `right_pressed` par un **système de “flanc montant”** :
  - Ajout de `key_just_pressed()` ou équivalent
  - Ajouter `up_pressed` / `down_pressed` (mêmes règles)

**Nouvelles méthodes :**

- `is_up_pressed()`, `is_down_pressed()` comme `is_left_pressed()` / `is_right_pressed()`, corrigées pour ne renvoyer `True` qu’une fois par appui

------

### 3. ✅ `game_engine.py`

**Fonction : `update()`**

- Modifier bloc de gestion des flèches :
  - `↑ ↓` → appel `player.scroll_items()`
  - `← →` → appel `player.scroll_weapons()`

------

### 4. ✅ `renderer.py`

**Fonction : `_render_inventory(player)`**

- Afficher les deux sections :
  - Gauche = `player.inventory_items`
  - Droite = `player.inventory_weapons`
- Pour les armes : ajouter le texte `x{ammo}` si présent

------

