"""
Service métier : Clients.
Toutes les opérations CRUD et requêtes liées aux clients.
Aucune dépendance à Streamlit — uniquement logique et accès base.
"""

from database.db import get_connection
from models.client import Client


def creer(client: Client) -> bool:
    """
    Crée un nouveau client.
    Retourne True si succès, False si validation échouée.
    """
    conn = get_connection()
    conn.execute(
        "INSERT INTO clients (nom, email, telephone, adresse, notes, date_creation) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        client.vers_tuple_insert(),
    )
    conn.commit()
    conn.close()
    return True


def modifier(client: Client) -> bool:
    """Met à jour un client existant."""
    conn = get_connection()
    conn.execute(
        "UPDATE clients SET nom=?, email=?, telephone=?, adresse=?, notes=? WHERE id=?",
        client.vers_tuple_update(),
    )
    conn.commit()
    conn.close()
    return True


def supprimer(client_id: int):
    """Supprime un client par son ID."""
    conn = get_connection()
    conn.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()


def obtenir(client_id: int) -> Client | None:
    """Retourne un client par son ID, ou None si introuvable."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    if row:
        return Client.depuis_dict(dict(row))
    return None


def lister(recherche: str = "") -> list[Client]:
    """
    Retourne tous les clients, triés par nom.
    Si `recherche` est renseigné, filtre sur nom/email/téléphone/adresse.
    """
    conn = get_connection()
    if recherche:
        motif = f"%{recherche}%"
        rows = conn.execute(
            "SELECT * FROM clients "
            "WHERE nom LIKE ? OR email LIKE ? OR telephone LIKE ? OR adresse LIKE ? "
            "ORDER BY nom",
            (motif, motif, motif, motif),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clients ORDER BY nom").fetchall()
    conn.close()
    return [Client.depuis_dict(dict(r)) for r in rows]


def compter() -> int:
    """Retourne le nombre total de clients."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    conn.close()
    return count


def lister_recents(limite: int = 5) -> list[Client]:
    """Retourne les derniers clients ajoutes, tries par date de creation descendante."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM clients ORDER BY date_creation DESC LIMIT ?",
        (limite,),
    ).fetchall()
    conn.close()
    return [Client.depuis_dict(dict(r)) for r in rows]


def lister_pour_selection() -> list[dict]:
    """
    Retourne une liste simplifiée {id, nom} pour les menus déroulants.
    Utilisé par les modules documents et outils.
    """
    conn = get_connection()
    rows = conn.execute("SELECT id, nom FROM clients ORDER BY nom").fetchall()
    conn.close()
    return [{"id": r["id"], "nom": r["nom"]} for r in rows]


def recherche_globale(terme: str) -> list[dict]:
    """Recherche un terme dans les clients pour la recherche globale."""
    motif = f"%{terme}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nom, email, telephone FROM clients "
        "WHERE nom LIKE ? OR email LIKE ? OR telephone LIKE ? OR notes LIKE ?",
        (motif, motif, motif, motif),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
