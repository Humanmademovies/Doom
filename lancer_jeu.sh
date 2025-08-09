#!/bin/bash

# Se déplace dans le répertoire du projet
cd "$(dirname "$0")"

# --- CORRECTION ---
# Chemin de base de votre installation Conda
CONDA_BASE_PATH="/media/old_disk/anaconda3"

# Active l'environnement Conda de la manière la plus fiable pour un script
source "${CONDA_BASE_PATH}/etc/profile.d/conda.sh"
conda activate doom

# Exécute le jeu
python3 main.py

# Laisse le terminal ouvert pour voir les messages
echo "Le script est terminé. Appuyez sur Entrée pour fermer la fenêtre."
read
