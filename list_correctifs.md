### Plan d’action détaillé ­— ajout de la gestion **munitions + mode de tir**

| Fichier                     | Fonctions **à créer / modifier / supprimer**                 | Rôle de la modification                                      |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **objects/weapon.py**       | • `__init__(…, ammo_type:str, mag_size:int, fire_mode:str="semi", rpm:int=400)` **(M)**  • `reload(player_ammo_pool)` **(C)**  • `can_fire(is_trigger_clicked, now)` **(N)**  • `fire(direction, from_position, now)` **(M)**  • `switch_fire_mode()` **(N)** | 1) stocke `ammo_loaded`, `ammo_reserve`, `last_shot_time`  ; 2) applique la logique *semi* / *auto* (cadence = 60 / rpm) ; 3) vérifie qu’un chargeur est disponible avant de tirer ; 4) permet aux armes hybrides d’activer/désactiver le mode “powered” si `ammo_type=="Battery"` |
| **objects/player.py**       | • attribut `self.ammo_pool: dict[str, int] = {}` **(N)**  • `reload_current_weapon()` **(N)**  • `pickup_weapon(item)` **(M)**  • `pickup_ammo(item)` **(N)**  • `fire_tick(now, input_mgr)` **(N)**  • `scroll_weapons()` **(M)** (ajouter prompt si > 4 armes) | Centralise les chargeurs par type ; déclenche rechargement (touche R) ; appelle `weapon.can_fire(...)` chaque frame ; gère la limite de 4 armes + drop sur la carte |
| **objects/item.py**         | • `on_pickup()` **(M)** (branche vers `player.pickup_weapon/ ammo`)  • nouvel `item_type=="ammo"` avec champs `ammo_type`, `amount` **(N)** | Distinction claire entre ramassage d’arme et de chargeur ; chaque arme ramassée fournit +1 chargeur. |
| **engine/input_manager.py** | • ajout `self._prev_mouse=False` dans `__init__` **(M)**  • dans `update()`: mémoriser l’état précédent **(M)**  • `is_mouse_clicked()` **(N)** → front montant (utile au semi)  • `is_mouse_held()` **(N)** → bouton maintenu | Expose les deux états dont la logique de tir a besoin.       |
| **engine/game_engine.py**   | • `update()` **(M)** :   – appeler `player.fire_tick(pygame.time.get_ticks()/1000, input_mgr)`   – touche `R` → `player.reload_current_weapon()` | La boucle principale n’appelle plus directement `perform_attack` ; tout passe par la logique munitions. |
| **engine/renderer.py**      | • `render_hud()` **(M)** : afficher `ammo_loaded / (spare × mag_size)` + pictogramme de calibre + label **AUTO/SEMI** | Feedback visuel complet sur la réserve et le mode de tir.    |
| **config.py**               | • définir constantes : `DEFAULT_MAG_SIZES`, `RPM_BY_WEAPON`, `MAX_WEAPONS=4` **(N)** | Paramètres globaux pour équilibrage facile.                  |
| **extras**                  | • (éventuel) `sounds/reload.wav`, `sounds/empty_click.wav`   | Retour sonore lors du rechargement et d’un tir à vide.       |

**Légende** : **(N)** = nouvelle fonction | **(M)** = fonction modifiée | **(S)** = fonction supprimée

------

#### Séquencement recommandé

1. **Étendre `Weapon`** (attributs + méthodes cadence/munitions).
2. **Mettre à jour `InputManager`** pour capter *click* vs *hold*.
3. **Refactoriser `Player`** (pool de munitions, tir, rechargement, limite de 4 armes).
4. **Adapter `Item.on_pickup`** pour gérer chargeurs et armes.
5. **Brancher `GameEngine.update`** sur la nouvelle API de tir.
6. **Augmenter le HUD** avec les informations de munitions et de mode de tir.
7. **Ajouter constantes dans `config.py`** et sons facultatifs.

Une fois tout compilé, les armes partageront leurs chargeurs par calibre, tireront au rythme défini (`rpm`) et respecteront un clic = un tir en *semi-auto*, ou un flux continu en *auto*.
