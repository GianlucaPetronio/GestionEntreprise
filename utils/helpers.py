"""
Utilitaires partagés par tous les modules.
Fonctions réutilisables pour l'application.
"""

import os
import uuid


# Chemin racine du projet (dossier contenant app.py)
RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chemin du dossier data
DATA_DIR = os.path.join(RACINE_PROJET, "data")

# Chemin de la base SQLite
DB_PATH = os.path.join(DATA_DIR, "gestion.db")

# Chemin du dossier d'upload
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")


def initialiser_dossiers():
    """Crée les dossiers nécessaires s'ils n'existent pas."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def generer_nom_fichier(nom_original: str) -> str:
    """
    Génère un nom de fichier unique (UUID) en conservant l'extension.
    Évite les collisions dans le dossier d'upload.
    """
    extension = os.path.splitext(nom_original)[1].lower()
    return f"{uuid.uuid4().hex}{extension}"


def chemin_fichier_upload(nom_fichier: str) -> str:
    """Retourne le chemin complet d'un fichier dans le dossier d'upload."""
    return os.path.join(UPLOAD_DIR, nom_fichier)


def fichier_existe(nom_fichier: str) -> bool:
    """Vérifie si un fichier uploadé existe sur le disque."""
    return os.path.isfile(chemin_fichier_upload(nom_fichier))


def supprimer_fichier_upload(nom_fichier: str) -> bool:
    """
    Supprime physiquement un fichier uploadé.
    Retourne True si supprimé, False si introuvable.
    """
    chemin = chemin_fichier_upload(nom_fichier)
    if os.path.isfile(chemin):
        os.remove(chemin)
        return True
    return False


def sauvegarder_fichier_upload(contenu: bytes, nom_fichier: str):
    """Écrit le contenu binaire dans le dossier d'upload."""
    chemin = chemin_fichier_upload(nom_fichier)
    with open(chemin, "wb") as f:
        f.write(contenu)


def formater_telephone(tel: str) -> str:
    """Formate un numéro de téléphone pour l'affichage (simple nettoyage)."""
    return tel.strip() if tel else ""


def valeur_ou_tiret(valeur: str) -> str:
    """Retourne la valeur ou un tiret si vide. Utilisé pour l'affichage."""
    return valeur.strip() if valeur and valeur.strip() else "—"
