"""
Service métier : Documents (GED).
Opérations CRUD, gestion des fichiers physiques et requêtes.
Aucune dépendance à Streamlit.
"""

from database.db import get_connection
from models.document import Document
from utils.helpers import (
    generer_nom_fichier,
    sauvegarder_fichier_upload,
    supprimer_fichier_upload,
)


def creer(document: Document, contenu_fichier: bytes) -> bool:
    """
    Crée un nouveau document :
    1. Génère un nom unique et sauvegarde le fichier sur disque
    2. Enregistre les métadonnées en base
    """
    # Générer le nom de stockage et sauvegarder le fichier
    nom_stockage = generer_nom_fichier(document.nom_original)
    sauvegarder_fichier_upload(contenu_fichier, nom_stockage)

    document.nom_fichier = nom_stockage
    conn = get_connection()
    conn.execute(
        "INSERT INTO documents "
        "(nom_fichier, nom_original, type_document, client_id, statut, notes, date_ajout) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        document.vers_tuple_insert(),
    )
    conn.commit()
    conn.close()
    return True


def modifier(document: Document) -> bool:
    """Met à jour les métadonnées d'un document (pas le fichier)."""
    conn = get_connection()
    conn.execute(
        "UPDATE documents SET type_document=?, client_id=?, statut=?, notes=? WHERE id=?",
        document.vers_tuple_update(),
    )
    conn.commit()
    conn.close()
    return True


def remplacer_fichier(doc_id: int, contenu_fichier: bytes, nom_original: str) -> bool:
    """
    Remplace le fichier physique d'un document existant.
    1. Supprime l'ancien fichier du disque
    2. Sauvegarde le nouveau fichier
    3. Met à jour nom_fichier et nom_original en base
    """
    conn = get_connection()
    row = conn.execute("SELECT nom_fichier FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        conn.close()
        return False

    # Supprimer l'ancien fichier
    supprimer_fichier_upload(row["nom_fichier"])

    # Sauvegarder le nouveau
    nouveau_nom = generer_nom_fichier(nom_original)
    sauvegarder_fichier_upload(contenu_fichier, nouveau_nom)

    # Mettre à jour en base
    conn.execute(
        "UPDATE documents SET nom_fichier=?, nom_original=? WHERE id=?",
        (nouveau_nom, nom_original, doc_id),
    )
    conn.commit()
    conn.close()
    return True


def supprimer(doc_id: int):
    """Supprime un document de la base ET le fichier physique du disque."""
    conn = get_connection()
    row = conn.execute("SELECT nom_fichier FROM documents WHERE id=?", (doc_id,)).fetchone()
    if row:
        supprimer_fichier_upload(row["nom_fichier"])
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()


def obtenir(doc_id: int) -> Document | None:
    """Retourne un document par son ID (avec le nom du client associé)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT d.*, c.nom AS nom_client "
        "FROM documents d LEFT JOIN clients c ON d.client_id = c.id "
        "WHERE d.id=?",
        (doc_id,),
    ).fetchone()
    conn.close()
    if row:
        return Document.depuis_dict(dict(row))
    return None


def lister(
    recherche: str = "",
    filtre_statut: str = "",
    filtre_client_id: int | None = None,
) -> list[Document]:
    """
    Retourne les documents avec filtres optionnels.
    Inclut le nom du client par jointure.
    """
    conn = get_connection()
    query = (
        "SELECT d.*, c.nom AS nom_client "
        "FROM documents d LEFT JOIN clients c ON d.client_id = c.id "
        "WHERE 1=1"
    )
    params: list = []

    if recherche:
        motif = f"%{recherche}%"
        query += " AND (d.nom_original LIKE ? OR d.type_document LIKE ? OR d.notes LIKE ?)"
        params.extend([motif, motif, motif])

    if filtre_statut:
        query += " AND d.statut = ?"
        params.append(filtre_statut)

    if filtre_client_id:
        query += " AND d.client_id = ?"
        params.append(filtre_client_id)

    query += " ORDER BY d.date_ajout DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [Document.depuis_dict(dict(r)) for r in rows]


def compter() -> int:
    """Retourne le nombre total de documents."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()
    return count


def compter_par_statut() -> dict[str, int]:
    """Retourne le nombre de documents groupés par statut."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT statut, COUNT(*) as total FROM documents GROUP BY statut"
    ).fetchall()
    conn.close()
    return {r["statut"]: r["total"] for r in rows}


def compter_pour_client(client_id: int) -> int:
    """Retourne le nombre de documents associés à un client."""
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE client_id=?", (client_id,)
    ).fetchone()[0]
    conn.close()
    return count


def recherche_globale(terme: str) -> list[dict]:
    """Recherche un terme dans les documents pour la recherche globale."""
    motif = f"%{terme}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT d.id, d.nom_original, d.type_document, d.statut, c.nom AS nom_client "
        "FROM documents d LEFT JOIN clients c ON d.client_id = c.id "
        "WHERE d.nom_original LIKE ? OR d.type_document LIKE ? OR d.notes LIKE ?",
        (motif, motif, motif),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
