"""
Modèle de données : Client.
Représentation objet d'un client avec validation.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Client:
    """Représente un client dans le système."""
    id: int = 0
    nom: str = ""
    email: str = ""
    telephone: str = ""
    adresse: str = ""
    notes: str = ""
    date_creation: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def valider(self) -> list[str]:
        """Valide les données du client. Retourne la liste des erreurs."""
        erreurs = []
        if not self.nom.strip():
            erreurs.append("Le nom du client est obligatoire.")
        return erreurs

    @staticmethod
    def depuis_dict(data: dict) -> "Client":
        """Crée un Client à partir d'un dictionnaire (ligne SQLite)."""
        return Client(
            id=data.get("id", 0),
            nom=data.get("nom", ""),
            email=data.get("email", ""),
            telephone=data.get("telephone", ""),
            adresse=data.get("adresse", ""),
            notes=data.get("notes", ""),
            date_creation=data.get("date_creation", ""),
        )

    def vers_tuple_insert(self) -> tuple:
        """Retourne un tuple pour l'insertion SQL (sans l'id)."""
        return (
            self.nom.strip(),
            self.email.strip(),
            self.telephone.strip(),
            self.adresse.strip(),
            self.notes.strip(),
            self.date_creation,
        )

    def vers_tuple_update(self) -> tuple:
        """Retourne un tuple pour la mise à jour SQL (id en dernier)."""
        return (
            self.nom.strip(),
            self.email.strip(),
            self.telephone.strip(),
            self.adresse.strip(),
            self.notes.strip(),
            self.id,
        )
