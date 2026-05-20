"""
Service d'integration Notion.
Synchronise les evenements avec une base de donnees Notion.
Necessite une cle API Notion et un ID de base de donnees.
"""

import json
import os
import urllib.request
import urllib.error

from models.event import Event

# Chemin du fichier de configuration Notion
_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "notion_config.json",
)

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def charger_config() -> dict:
    """Charge la configuration Notion depuis le fichier JSON."""
    if os.path.isfile(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"api_key": "", "database_id": "", "active": False}


def sauvegarder_config(config: dict):
    """Sauvegarde la configuration Notion."""
    os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def est_configure() -> bool:
    """Verifie si l'integration Notion est configuree et active."""
    config = charger_config()
    return bool(config.get("active") and config.get("api_key") and config.get("database_id"))


def _headers(api_key: str) -> dict:
    """Retourne les en-tetes HTTP pour l'API Notion."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def tester_connexion(api_key: str, database_id: str) -> tuple[bool, str]:
    """
    Teste la connexion a la base Notion.
    Retourne (succes, message).
    """
    try:
        url = f"{NOTION_API_URL}/databases/{database_id}"
        req = urllib.request.Request(url, headers=_headers(api_key), method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "Connexion reussie."
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "Cle API invalide."
        elif e.code == 404:
            return False, "Base de donnees introuvable. Verifiez l'ID et le partage avec l'integration."
        return False, f"Erreur HTTP {e.code}."
    except urllib.error.URLError as e:
        return False, f"Erreur reseau : {e.reason}"
    except Exception as e:
        return False, f"Erreur : {str(e)}"
    return False, "Erreur inconnue."


def synchroniser_event(event: Event) -> tuple[bool, str]:
    """
    Exporte un evenement vers la base Notion.
    Retourne (succes, message).
    """
    config = charger_config()
    if not config.get("active"):
        return False, "Integration Notion desactivee."

    api_key = config["api_key"]
    database_id = config["database_id"]

    # Construire les proprietes Notion
    properties = {
        "Titre": {
            "title": [{"text": {"content": event.titre}}]
        },
        "Date": {
            "date": {
                "start": event.date_debut.replace(" ", "T") if event.date_debut else None,
                "end": event.date_fin.replace(" ", "T") if event.date_fin else None,
            }
        },
        "Statut": {
            "select": {"name": event.statut_label}
        },
    }

    if event.client_nom:
        properties["Client"] = {
            "rich_text": [{"text": {"content": event.client_nom}}]
        }

    if event.type_travail:
        properties["Type"] = {
            "select": {"name": event.type_label}
        }

    payload = json.dumps({
        "parent": {"database_id": database_id},
        "properties": properties,
    }).encode("utf-8")

    try:
        url = f"{NOTION_API_URL}/pages"
        req = urllib.request.Request(url, data=payload, headers=_headers(api_key), method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "Evenement synchronise avec Notion."
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return False, f"Erreur Notion ({e.code}) : {body[:200]}"
    except urllib.error.URLError as e:
        return False, f"Erreur reseau : {e.reason}"
    except Exception as e:
        return False, f"Erreur : {str(e)}"
    return False, "Erreur inconnue."


def synchroniser_tous_les_events(events: list[Event]) -> tuple[int, int, list[str]]:
    """
    Synchronise une liste d'evenements vers Notion.
    Retourne (nb_succes, nb_erreurs, messages_erreurs).
    """
    succes = 0
    erreurs = 0
    messages = []

    for ev in events:
        ok, msg = synchroniser_event(ev)
        if ok:
            succes += 1
        else:
            erreurs += 1
            messages.append(f"{ev.titre}: {msg}")

    return succes, erreurs, messages
