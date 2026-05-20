"""
Modèle de données : Document.
Représentation objet d'un document GED avec validation.
"""

from dataclasses import dataclass, field
from datetime import datetime

# Constantes partagées pour les statuts et types de documents
STATUTS = {
    "recu": "Reçu",
    "en_cours": "En cours",
    "envoye": "Envoyé",
    "archive": "Archivé",
}

TYPES = [
    "Devis",
    "Facture client",
    "Facture fournisseur",
    "Bon de commande",
    "Bon de livraison",
    "Ticket de caisse",
    "Contrat",
    "Photo chantier",
    "Plan",
    "Attestation",
    "Assurance",
    "Administratif",
    "Autre",
]

# Extensions autorisées pour l'upload
EXTENSIONS_AUTORISEES = [
    "pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp",
    "doc", "docx", "xls", "xlsx", "csv", "txt", "zip",
]


@dataclass
class Document:
    """Représente un document dans le système GED."""
    id: int = 0
    nom_fichier: str = ""       # Nom unique sur le disque (UUID)
    nom_original: str = ""      # Nom original du fichier uploadé
    type_document: str = ""
    client_id: int | None = None
    statut: str = "recu"
    notes: str = ""
    date_ajout: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    # Champ virtuel (jointure) — pas en base
    nom_client: str = ""

    def valider(self) -> list[str]:
        """Valide les données du document. Retourne la liste des erreurs."""
        erreurs = []
        if not self.nom_original.strip():
            erreurs.append("Le fichier est obligatoire.")
        if self.statut not in STATUTS:
            erreurs.append("Statut invalide.")
        return erreurs

    @staticmethod
    def depuis_dict(data: dict) -> "Document":
        """Crée un Document à partir d'un dictionnaire (ligne SQLite)."""
        return Document(
            id=data.get("id", 0),
            nom_fichier=data.get("nom_fichier", ""),
            nom_original=data.get("nom_original", ""),
            type_document=data.get("type_document", ""),
            client_id=data.get("client_id"),
            statut=data.get("statut", "recu"),
            notes=data.get("notes", ""),
            date_ajout=data.get("date_ajout", ""),
            nom_client=data.get("nom_client", "") or "",
        )

    def vers_tuple_insert(self) -> tuple:
        """Tuple pour l'insertion SQL."""
        return (
            self.nom_fichier,
            self.nom_original,
            self.type_document,
            self.client_id if self.client_id else None,
            self.statut,
            self.notes.strip(),
            self.date_ajout,
        )

    def vers_tuple_update(self) -> tuple:
        """Tuple pour la mise à jour SQL (id en dernier)."""
        return (
            self.type_document,
            self.client_id if self.client_id else None,
            self.statut,
            self.notes.strip(),
            self.id,
        )

    @property
    def statut_label(self) -> str:
        """Retourne le libellé lisible du statut."""
        return STATUTS.get(self.statut, self.statut)

    @property
    def est_image(self) -> bool:
        """Vérifie si le fichier est une image affichable."""
        ext = self.nom_original.rsplit(".", 1)[-1].lower() if "." in self.nom_original else ""
        return ext in ("png", "jpg", "jpeg", "gif", "bmp", "webp")
