"""
Service metier : Factures.
Operations CRUD et requetes liees aux factures.
Aucune dependance a Streamlit.
"""

from database.db import get_connection
from models.invoice import Invoice


def creer(invoice: Invoice) -> int:
    """Cree une nouvelle facture. Retourne l'id cree."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO invoices (event_id, client_id, description, montant, statut, date_creation) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        invoice.vers_tuple_insert(),
    )
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return invoice_id


def modifier(invoice: Invoice) -> bool:
    """Met a jour une facture existante."""
    conn = get_connection()
    conn.execute(
        "UPDATE invoices SET event_id=?, client_id=?, description=?, montant=?, statut=? "
        "WHERE id=?",
        invoice.vers_tuple_update(),
    )
    conn.commit()
    conn.close()
    return True


def supprimer(invoice_id: int):
    """Supprime une facture par son ID."""
    conn = get_connection()
    conn.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
    conn.commit()
    conn.close()


def obtenir(invoice_id: int) -> Invoice | None:
    """Retourne une facture par son ID avec noms client et evenement."""
    conn = get_connection()
    row = conn.execute(
        "SELECT i.*, c.nom AS client_nom, e.titre AS event_titre "
        "FROM invoices i "
        "LEFT JOIN clients c ON i.client_id = c.id "
        "LEFT JOIN events e ON i.event_id = e.id "
        "WHERE i.id=?",
        (invoice_id,),
    ).fetchone()
    conn.close()
    if row:
        return Invoice.depuis_dict(dict(row))
    return None


def lister(recherche: str = "", filtre_statut: str = "", filtre_client_id: int | None = None) -> list[Invoice]:
    """Retourne les factures avec filtres optionnels."""
    conn = get_connection()
    query = (
        "SELECT i.*, c.nom AS client_nom, e.titre AS event_titre "
        "FROM invoices i "
        "LEFT JOIN clients c ON i.client_id = c.id "
        "LEFT JOIN events e ON i.event_id = e.id "
        "WHERE 1=1"
    )
    params: list = []

    if recherche:
        motif = f"%{recherche}%"
        query += " AND (i.description LIKE ? OR c.nom LIKE ?)"
        params.extend([motif, motif])

    if filtre_statut:
        query += " AND i.statut = ?"
        params.append(filtre_statut)

    if filtre_client_id:
        query += " AND i.client_id = ?"
        params.append(filtre_client_id)

    query += " ORDER BY i.date_creation DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [Invoice.depuis_dict(dict(r)) for r in rows]


def lister_pour_event(event_id: int) -> list[Invoice]:
    """Retourne les factures liees a un evenement."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT i.*, c.nom AS client_nom, e.titre AS event_titre "
        "FROM invoices i "
        "LEFT JOIN clients c ON i.client_id = c.id "
        "LEFT JOIN events e ON i.event_id = e.id "
        "WHERE i.event_id = ? ORDER BY i.date_creation DESC",
        (event_id,),
    ).fetchall()
    conn.close()
    return [Invoice.depuis_dict(dict(r)) for r in rows]


def compter() -> int:
    """Retourne le nombre total de factures."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
    conn.close()
    return count


def compter_par_statut() -> dict[str, int]:
    """Retourne le nombre de factures groupees par statut."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT statut, COUNT(*) as total FROM invoices GROUP BY statut"
    ).fetchall()
    conn.close()
    return {r["statut"]: r["total"] for r in rows}


def total_montant_par_statut() -> dict[str, float]:
    """Retourne le montant total des factures groupees par statut."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT statut, SUM(montant) as total FROM invoices GROUP BY statut"
    ).fetchall()
    conn.close()
    return {r["statut"]: r["total"] or 0.0 for r in rows}


def recherche_globale(terme: str) -> list[dict]:
    """Recherche un terme dans les factures pour la recherche globale."""
    motif = f"%{terme}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT i.id, i.description, i.montant, i.statut, c.nom AS client_nom "
        "FROM invoices i LEFT JOIN clients c ON i.client_id = c.id "
        "WHERE i.description LIKE ? OR c.nom LIKE ?",
        (motif, motif),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
