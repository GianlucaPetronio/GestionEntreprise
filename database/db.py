"""
Module de connexion et d'initialisation de la base de données SQLite.
Responsabilité unique : gérer la connexion et créer le schéma.
"""

import sqlite3
from utils.helpers import DB_PATH, initialiser_dossiers


def get_connection() -> sqlite3.Connection:
    """
    Retourne une connexion SQLite configurée.
    - row_factory = Row pour accéder aux colonnes par nom
    - foreign_keys activées
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Initialise la base de données :
    1. Crée les dossiers data/ et data/uploads/
    2. Crée les tables si elles n'existent pas
    """
    initialiser_dossiers()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nom             TEXT    NOT NULL,
            email           TEXT    DEFAULT '',
            telephone       TEXT    DEFAULT '',
            adresse         TEXT    DEFAULT '',
            notes           TEXT    DEFAULT '',
            date_creation   TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_fichier     TEXT    NOT NULL,
            nom_original    TEXT    NOT NULL,
            type_document   TEXT    DEFAULT '',
            client_id       INTEGER,
            statut          TEXT    DEFAULT 'recu',
            notes           TEXT    DEFAULT '',
            date_ajout      TEXT    NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outils (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nom             TEXT    NOT NULL,
            description     TEXT    DEFAULT '',
            etat            TEXT    DEFAULT 'disponible',
            assignation     TEXT    DEFAULT '',
            date_ajout      TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            titre           TEXT    NOT NULL,
            description     TEXT    DEFAULT '',
            date_debut      TEXT    NOT NULL,
            date_fin        TEXT    NOT NULL,
            client_id       INTEGER,
            type_travail    TEXT    DEFAULT '',
            statut          TEXT    DEFAULT 'planifie',
            notes           TEXT    DEFAULT '',
            date_creation   TEXT    NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_tools (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id        INTEGER NOT NULL,
            outil_id        INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
            FOREIGN KEY (outil_id) REFERENCES outils(id) ON DELETE CASCADE,
            UNIQUE(event_id, outil_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id        INTEGER,
            client_id       INTEGER,
            description     TEXT    DEFAULT '',
            montant         REAL    DEFAULT 0.0,
            statut          TEXT    DEFAULT 'brouillon',
            date_creation   TEXT    NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
        )
    """)

    conn.commit()
    conn.close()
