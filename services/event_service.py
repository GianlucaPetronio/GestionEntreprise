"""
Service metier : Evenements (Agenda).
Operations CRUD et requetes liees aux evenements.
Aucune dependance a Streamlit.
"""

from database.db import get_connection
from models.event import Event


def creer(event: Event) -> int:
    """
    Cree un nouvel evenement.
    Retourne l'id de l'evenement cree.
    """
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO events (titre, description, date_debut, date_fin, client_id, "
        "type_travail, statut, notes, date_creation) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        event.vers_tuple_insert(),
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id


def modifier(event: Event) -> bool:
    """Met a jour un evenement existant."""
    conn = get_connection()
    conn.execute(
        "UPDATE events SET titre=?, description=?, date_debut=?, date_fin=?, "
        "client_id=?, type_travail=?, statut=?, notes=? WHERE id=?",
        event.vers_tuple_update(),
    )
    conn.commit()
    conn.close()
    return True


def supprimer(event_id: int):
    """Supprime un evenement par son ID (cascade sur event_tools)."""
    conn = get_connection()
    conn.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()


def obtenir(event_id: int) -> Event | None:
    """Retourne un evenement par son ID avec le nom du client."""
    conn = get_connection()
    row = conn.execute(
        "SELECT e.*, c.nom AS client_nom "
        "FROM events e LEFT JOIN clients c ON e.client_id = c.id "
        "WHERE e.id=?",
        (event_id,),
    ).fetchone()
    if not row:
        conn.close()
        return None
    event = Event.depuis_dict(dict(row))
    # Charger les outils associes
    outils_rows = conn.execute(
        "SELECT o.nom FROM event_tools et "
        "JOIN outils o ON et.outil_id = o.id "
        "WHERE et.event_id = ?",
        (event_id,),
    ).fetchall()
    event.outils_noms = [r["nom"] for r in outils_rows]
    conn.close()
    return event


def lister(recherche: str = "", filtre_statut: str = "", filtre_client_id: int | None = None) -> list[Event]:
    """
    Retourne les evenements avec filtres optionnels.
    Tries par date_debut descendante.
    """
    conn = get_connection()
    query = (
        "SELECT e.*, c.nom AS client_nom "
        "FROM events e LEFT JOIN clients c ON e.client_id = c.id "
        "WHERE 1=1"
    )
    params: list = []

    if recherche:
        motif = f"%{recherche}%"
        query += " AND (e.titre LIKE ? OR e.description LIKE ? OR e.notes LIKE ?)"
        params.extend([motif, motif, motif])

    if filtre_statut:
        query += " AND e.statut = ?"
        params.append(filtre_statut)

    if filtre_client_id:
        query += " AND e.client_id = ?"
        params.append(filtre_client_id)

    query += " ORDER BY e.date_debut DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [Event.depuis_dict(dict(r)) for r in rows]


def lister_par_periode(date_start: str, date_end: str, filtre_client_id: int | None = None) -> list[Event]:
    """
    Retourne les evenements dans une periode donnee.
    date_start et date_end au format YYYY-MM-DD.
    """
    conn = get_connection()
    query = (
        "SELECT e.*, c.nom AS client_nom "
        "FROM events e LEFT JOIN clients c ON e.client_id = c.id "
        "WHERE e.date_debut >= ? AND e.date_debut < ?"
    )
    params: list = [date_start, date_end]

    if filtre_client_id:
        query += " AND e.client_id = ?"
        params.append(filtre_client_id)

    query += " ORDER BY e.date_debut ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [Event.depuis_dict(dict(r)) for r in rows]


def compter() -> int:
    """Retourne le nombre total d'evenements."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    return count


def compter_par_statut() -> dict[str, int]:
    """Retourne le nombre d'evenements groupes par statut."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT statut, COUNT(*) as total FROM events GROUP BY statut"
    ).fetchall()
    conn.close()
    return {r["statut"]: r["total"] for r in rows}


def evenements_a_venir(limite: int = 5) -> list[Event]:
    """Retourne les prochains evenements planifies ou en cours (a partir d'aujourd'hui)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT e.*, c.nom AS client_nom "
        "FROM events e LEFT JOIN clients c ON e.client_id = c.id "
        "WHERE e.statut IN ('planifie', 'en_cours') "
        "AND e.date_debut >= date('now') "
        "ORDER BY e.date_debut ASC LIMIT ?",
        (limite,),
    ).fetchall()
    conn.close()
    return [Event.depuis_dict(dict(r)) for r in rows]


# --- Gestion des outils associes ---

def associer_outils(event_id: int, outil_ids: list[int]):
    """Associe une liste d'outils a un evenement (remplace les existants)."""
    conn = get_connection()
    conn.execute("DELETE FROM event_tools WHERE event_id = ?", (event_id,))
    for oid in outil_ids:
        conn.execute(
            "INSERT OR IGNORE INTO event_tools (event_id, outil_id) VALUES (?, ?)",
            (event_id, oid),
        )
    conn.commit()
    conn.close()


def obtenir_outils_ids(event_id: int) -> list[int]:
    """Retourne les IDs des outils associes a un evenement."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT outil_id FROM event_tools WHERE event_id = ?",
        (event_id,),
    ).fetchall()
    conn.close()
    return [r["outil_id"] for r in rows]


def recherche_globale(terme: str) -> list[dict]:
    """Recherche un terme dans les evenements pour la recherche globale."""
    motif = f"%{terme}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT e.id, e.titre, e.date_debut, e.statut, c.nom AS client_nom "
        "FROM events e LEFT JOIN clients c ON e.client_id = c.id "
        "WHERE e.titre LIKE ? OR e.description LIKE ? OR e.notes LIKE ?",
        (motif, motif, motif),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
