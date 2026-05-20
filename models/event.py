"""
Modele de donnees : Evenement (Agenda).
Representation objet d'un evenement avec validation.
"""

from dataclasses import dataclass, field
from datetime import datetime


STATUTS = {
    "planifie": "Planifie",
    "en_cours": "En cours",
    "termine": "Termine",
    "annule": "Annule",
}

STATUTS_ICONES = {
    "planifie": "📅",
    "en_cours": "🔄",
    "termine": "✅",
    "annule": "❌",
}

TYPES_TRAVAIL = {
    "entretien": "Entretien",
    "tonte": "Tonte",
    "taille": "Taille",
    "debroussaillage": "Debroussaillage",
    "nettoyage": "Nettoyage",
    "plantation": "Plantation",
    "amenagement": "Amenagement",
    "autre": "Autre",
}


@dataclass
class Event:
    """Represente un evenement dans l'agenda."""
    id: int = 0
    titre: str = ""
    description: str = ""
    date_debut: str = ""
    date_fin: str = ""
    client_id: int | None = None
    type_travail: str = ""
    statut: str = "planifie"
    notes: str = ""
    date_creation: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    # Champs supplementaires charges par les requetes JOIN
    client_nom: str = ""
    outils_noms: list = field(default_factory=list)

    def valider(self) -> list[str]:
        """Valide les donnees de l'evenement. Retourne la liste des erreurs."""
        erreurs = []
        if not self.titre.strip():
            erreurs.append("Le titre est obligatoire.")
        if not self.date_debut:
            erreurs.append("La date de debut est obligatoire.")
        if not self.date_fin:
            erreurs.append("La date de fin est obligatoire.")
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            erreurs.append("La date de fin doit etre apres la date de debut.")
        if self.statut not in STATUTS:
            erreurs.append("Statut invalide.")
        return erreurs

    @staticmethod
    def depuis_dict(data: dict) -> "Event":
        """Cree un Event a partir d'un dictionnaire (ligne SQLite)."""
        return Event(
            id=data.get("id", 0),
            titre=data.get("titre", ""),
            description=data.get("description", ""),
            date_debut=data.get("date_debut", ""),
            date_fin=data.get("date_fin", ""),
            client_id=data.get("client_id"),
            type_travail=data.get("type_travail", ""),
            statut=data.get("statut", "planifie"),
            notes=data.get("notes", ""),
            date_creation=data.get("date_creation", ""),
            client_nom=data.get("client_nom") or "",
        )

    def vers_tuple_insert(self) -> tuple:
        """Retourne un tuple pour l'insertion SQL (sans l'id)."""
        return (
            self.titre.strip(),
            self.description.strip(),
            self.date_debut,
            self.date_fin,
            self.client_id,
            self.type_travail,
            self.statut,
            self.notes.strip(),
            self.date_creation,
        )

    def vers_tuple_update(self) -> tuple:
        """Retourne un tuple pour la mise a jour SQL (id en dernier)."""
        return (
            self.titre.strip(),
            self.description.strip(),
            self.date_debut,
            self.date_fin,
            self.client_id,
            self.type_travail,
            self.statut,
            self.notes.strip(),
            self.id,
        )

    @property
    def statut_label(self) -> str:
        return STATUTS.get(self.statut, self.statut)

    @property
    def statut_icone(self) -> str:
        return STATUTS_ICONES.get(self.statut, "")

    @property
    def type_label(self) -> str:
        return TYPES_TRAVAIL.get(self.type_travail, self.type_travail)
