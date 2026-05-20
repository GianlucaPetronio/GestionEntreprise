"""
Modèle de données : Outil / Équipement.
Représentation objet d'un outil avec validation.
"""

from dataclasses import dataclass, field
from datetime import datetime

# Constantes partagées pour les états
ETATS = {
    "disponible": "Disponible",
    "utilise": "En utilisation",
    "maintenance": "En maintenance",
}

ETATS_ICONES = {
    "disponible": "🟢",
    "utilise": "🔵",
    "maintenance": "🟠",
}


@dataclass
class Outil:
    """Représente un outil ou équipement."""
    id: int = 0
    nom: str = ""
    description: str = ""
    etat: str = "disponible"
    assignation: str = ""
    date_ajout: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def valider(self) -> list[str]:
        """Valide les données de l'outil. Retourne la liste des erreurs."""
        erreurs = []
        if not self.nom.strip():
            erreurs.append("Le nom de l'outil est obligatoire.")
        if self.etat not in ETATS:
            erreurs.append("État invalide.")
        return erreurs

    @staticmethod
    def depuis_dict(data: dict) -> "Outil":
        """Crée un Outil à partir d'un dictionnaire (ligne SQLite)."""
        return Outil(
            id=data.get("id", 0),
            nom=data.get("nom", ""),
            description=data.get("description", ""),
            etat=data.get("etat", "disponible"),
            assignation=data.get("assignation", ""),
            date_ajout=data.get("date_ajout", ""),
        )

    def vers_tuple_insert(self) -> tuple:
        """Tuple pour l'insertion SQL."""
        return (
            self.nom.strip(),
            self.description.strip(),
            self.etat,
            self.assignation.strip(),
            self.date_ajout,
        )

    def vers_tuple_update(self) -> tuple:
        """Tuple pour la mise à jour SQL (id en dernier)."""
        return (
            self.nom.strip(),
            self.description.strip(),
            self.etat,
            self.assignation.strip(),
            self.id,
        )

    @property
    def etat_label(self) -> str:
        """Retourne le libellé lisible de l'état."""
        return ETATS.get(self.etat, self.etat)

    @property
    def etat_icone(self) -> str:
        """Retourne l'icône associée à l'état."""
        return ETATS_ICONES.get(self.etat, "")
