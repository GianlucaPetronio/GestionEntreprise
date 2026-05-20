"""
Modele de donnees : Facture.
Representation objet d'une facture liee a un evenement.
"""

from dataclasses import dataclass, field
from datetime import datetime


STATUTS = {
    "brouillon": "Brouillon",
    "en_attente": "En attente",
    "paye": "Paye",
}

STATUTS_ICONES = {
    "brouillon": "📝",
    "en_attente": "⏳",
    "paye": "✅",
}


@dataclass
class Invoice:
    """Represente une facture."""
    id: int = 0
    event_id: int | None = None
    client_id: int | None = None
    description: str = ""
    montant: float = 0.0
    statut: str = "brouillon"
    date_creation: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    # Champs supplementaires charges par JOIN
    client_nom: str = ""
    event_titre: str = ""

    def valider(self) -> list[str]:
        """Valide les donnees de la facture. Retourne la liste des erreurs."""
        erreurs = []
        if not self.description.strip():
            erreurs.append("La description est obligatoire.")
        if self.montant < 0:
            erreurs.append("Le montant ne peut pas etre negatif.")
        if self.statut not in STATUTS:
            erreurs.append("Statut invalide.")
        return erreurs

    @staticmethod
    def depuis_dict(data: dict) -> "Invoice":
        """Cree une Invoice a partir d'un dictionnaire (ligne SQLite)."""
        return Invoice(
            id=data.get("id", 0),
            event_id=data.get("event_id"),
            client_id=data.get("client_id"),
            description=data.get("description", ""),
            montant=data.get("montant", 0.0),
            statut=data.get("statut", "brouillon"),
            date_creation=data.get("date_creation", ""),
            client_nom=data.get("client_nom") or "",
            event_titre=data.get("event_titre") or "",
        )

    def vers_tuple_insert(self) -> tuple:
        """Tuple pour l'insertion SQL (sans l'id)."""
        return (
            self.event_id,
            self.client_id,
            self.description.strip(),
            self.montant,
            self.statut,
            self.date_creation,
        )

    def vers_tuple_update(self) -> tuple:
        """Tuple pour la mise a jour SQL (id en dernier)."""
        return (
            self.event_id,
            self.client_id,
            self.description.strip(),
            self.montant,
            self.statut,
            self.id,
        )

    @property
    def statut_label(self) -> str:
        return STATUTS.get(self.statut, self.statut)

    @property
    def statut_icone(self) -> str:
        return STATUTS_ICONES.get(self.statut, "")

    @property
    def montant_formate(self) -> str:
        return f"{self.montant:.2f} EUR"
