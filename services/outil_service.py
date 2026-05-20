"""
Service métier : Outils / Équipements.
Opérations CRUD et requêtes liées aux outils.
Aucune dépendance à Streamlit.
"""

from database.db import get_connection
from models.outil import Outil


def creer(outil: Outil) -> bool:
    """Crée un nouvel outil en base."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO outils (nom, description, etat, assignation, date_ajout) "
        "VALUES (?, ?, ?, ?, ?)",
        outil.vers_tuple_insert(),
    )
    conn.commit()
    conn.close()
    return True


def modifier(outil: Outil) -> bool:
    """Met à jour un outil existant."""
    conn = get_connection()
    conn.execute(
        "UPDATE outils SET nom=?, description=?, etat=?, assignation=? WHERE id=?",
        outil.vers_tuple_update(),
    )
    conn.commit()
    conn.close()
    return True


def supprimer(outil_id: int):
    """Supprime un outil par son ID."""
    conn = get_connection()
    conn.execute("DELETE FROM outils WHERE id=?", (outil_id,))
    conn.commit()
    conn.close()


def obtenir(outil_id: int) -> Outil | None:
    """Retourne un outil par son ID, ou None si introuvable."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM outils WHERE id=?", (outil_id,)).fetchone()
    conn.close()
    if row:
        return Outil.depuis_dict(dict(row))
    return None


def lister(recherche: str = "", filtre_etat: str = "") -> list[Outil]:
    """
    Retourne les outils avec filtres optionnels.
    Triés par nom.
    """
    conn = get_connection()
    query = "SELECT * FROM outils WHERE 1=1"
    params: list = []

    if recherche:
        motif = f"%{recherche}%"
        query += " AND (nom LIKE ? OR description LIKE ? OR assignation LIKE ?)"
        params.extend([motif, motif, motif])

    if filtre_etat:
        query += " AND etat = ?"
        params.append(filtre_etat)

    query += " ORDER BY nom"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [Outil.depuis_dict(dict(r)) for r in rows]


def compter() -> int:
    """Retourne le nombre total d'outils."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM outils").fetchone()[0]
    conn.close()
    return count


def compter_par_etat() -> dict[str, int]:
    """Retourne le nombre d'outils groupés par état."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT etat, COUNT(*) as total FROM outils GROUP BY etat"
    ).fetchall()
    conn.close()
    return {r["etat"]: r["total"] for r in rows}


def recherche_globale(terme: str) -> list[dict]:
    """Recherche un terme dans les outils pour la recherche globale."""
    motif = f"%{terme}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nom, description, etat FROM outils "
        "WHERE nom LIKE ? OR description LIKE ? OR assignation LIKE ?",
        (motif, motif, motif),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
