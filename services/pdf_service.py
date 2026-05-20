"""
Service de generation de factures PDF.
Utilise fpdf2 pour generer des factures professionnelles
a partir d'un template pre-defini.
"""

import json
import os
from datetime import datetime

from fpdf import FPDF

from models.invoice import Invoice

# Chemin du fichier de configuration entreprise
_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "entreprise_config.json",
)

DEFAULT_CONFIG = {
    "nom": "GP Entretien Exterieurs",
    "adresse": "",
    "code_postal": "",
    "ville": "",
    "telephone": "",
    "email": "",
    "siret": "",
    "mention_legale": "Auto-entrepreneur - TVA non applicable, art. 293 B du CGI",
}


def charger_config() -> dict:
    """Charge la configuration entreprise."""
    if os.path.isfile(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        # Fusionner avec les valeurs par defaut
        config = dict(DEFAULT_CONFIG)
        config.update(saved)
        return config
    return dict(DEFAULT_CONFIG)


def sauvegarder_config(config: dict):
    """Sauvegarde la configuration entreprise."""
    os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


class FacturePDF(FPDF):
    """PDF de facture avec template professionnel."""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        # --- Bandeau vert en haut ---
        self.set_fill_color(30, 107, 32)  # Vert fonce
        self.rect(0, 0, 210, 8, "F")

        # --- Logo / Nom entreprise ---
        self.set_y(15)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(30, 107, 32)
        self.cell(0, 10, self.config.get("nom", ""), new_x="LMARGIN", new_y="NEXT")

        # --- Coordonnees entreprise ---
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)

        lignes = []
        if self.config.get("adresse"):
            lignes.append(self.config["adresse"])
        cp_ville = f"{self.config.get('code_postal', '')} {self.config.get('ville', '')}".strip()
        if cp_ville:
            lignes.append(cp_ville)
        if self.config.get("telephone"):
            lignes.append(f"Tel : {self.config['telephone']}")
        if self.config.get("email"):
            lignes.append(f"Email : {self.config['email']}")
        if self.config.get("siret"):
            lignes.append(f"SIRET : {self.config['siret']}")

        for ligne in lignes:
            self.cell(0, 4, ligne, new_x="LMARGIN", new_y="NEXT")

        self.ln(5)

    def footer(self):
        self.set_y(-20)
        # --- Ligne separatrice ---
        self.set_draw_color(30, 107, 32)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        # --- Mention legale ---
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(130, 130, 130)
        mention = self.config.get("mention_legale", "")
        if mention:
            self.cell(0, 4, mention, align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 4, f"Document genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", align="C")


def generer_facture_pdf(invoice: Invoice, lignes_prestation: list[dict] | None = None) -> bytes:
    """
    Genere un PDF de facture.

    Args:
        invoice: L'objet facture avec les donnees.
        lignes_prestation: Liste optionnelle de lignes detaillees.
            Chaque element : {"description": str, "quantite": float, "prix_unitaire": float}
            Si None, une seule ligne est creee depuis invoice.description et invoice.montant.

    Returns:
        Le contenu du PDF en bytes.
    """
    config = charger_config()
    pdf = FacturePDF(config)
    pdf.add_page()

    # --- Numero et date de facture ---
    y_start = pdf.get_y()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(50, 50, 50)
    numero = f"FAC-{invoice.id:04d}"
    pdf.cell(0, 10, f"FACTURE {numero}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    date_str = invoice.date_creation[:10] if invoice.date_creation else datetime.now().strftime("%Y-%m-%d")
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date_affichee = date_obj.strftime("%d/%m/%Y")
    except ValueError:
        date_affichee = date_str
    pdf.cell(0, 6, f"Date : {date_affichee}", new_x="LMARGIN", new_y="NEXT")

    # Statut
    statut_label = invoice.statut_label
    pdf.cell(0, 6, f"Statut : {statut_label}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    # --- Bloc client ---
    if invoice.client_nom:
        pdf.set_fill_color(245, 247, 250)
        pdf.set_draw_color(200, 200, 200)

        x_client = 120
        pdf.set_xy(x_client, y_start)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 107, 32)
        pdf.cell(80, 6, "FACTURER A :", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(x_client)

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(80, 7, invoice.client_nom, new_x="LMARGIN", new_y="NEXT")

        pdf.set_xy(10, max(pdf.get_y() + 5, y_start + 35))

    # --- Evenement lie ---
    if invoice.event_titre:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Evenement lie : {invoice.event_titre}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.ln(5)

    # --- Tableau des prestations ---
    # En-tete du tableau
    pdf.set_fill_color(30, 107, 32)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_draw_color(30, 107, 32)

    col_desc = 95
    col_qty = 25
    col_pu = 35
    col_total = 35

    pdf.cell(col_desc, 8, "  Description", border=1, fill=True)
    pdf.cell(col_qty, 8, "Qte", border=1, fill=True, align="C")
    pdf.cell(col_pu, 8, "Prix unit.", border=1, fill=True, align="C")
    pdf.cell(col_total, 8, "Total", border=1, fill=True, align="C")
    pdf.ln()

    # Lignes de prestation
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_draw_color(220, 220, 220)

    total_general = 0.0

    if lignes_prestation:
        for i, ligne in enumerate(lignes_prestation):
            desc = ligne.get("description", "")
            qty = ligne.get("quantite", 1)
            pu = ligne.get("prix_unitaire", 0.0)
            total_ligne = qty * pu
            total_general += total_ligne

            bg = (i % 2 == 0)
            if bg:
                pdf.set_fill_color(250, 252, 250)

            pdf.cell(col_desc, 7, f"  {desc}", border="LR", fill=bg)
            pdf.cell(col_qty, 7, f"{qty}", border="LR", fill=bg, align="C")
            pdf.cell(col_pu, 7, f"{pu:.2f} EUR", border="LR", fill=bg, align="R")
            pdf.cell(col_total, 7, f"{total_ligne:.2f} EUR", border="LR", fill=bg, align="R")
            pdf.ln()
    else:
        # Ligne unique depuis les donnees de la facture
        desc = invoice.description or "Prestation"
        total_general = invoice.montant

        pdf.set_fill_color(250, 252, 250)
        pdf.cell(col_desc, 7, f"  {desc}", border="LR", fill=True)
        pdf.cell(col_qty, 7, "1", border="LR", fill=True, align="C")
        pdf.cell(col_pu, 7, f"{invoice.montant:.2f} EUR", border="LR", fill=True, align="R")
        pdf.cell(col_total, 7, f"{invoice.montant:.2f} EUR", border="LR", fill=True, align="R")
        pdf.ln()

    # Ligne de fermeture du tableau
    pdf.cell(col_desc + col_qty + col_pu + col_total, 0, "", border="T")
    pdf.ln(5)

    # --- Total ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 107, 32)
    x_total = 10 + col_desc + col_qty
    pdf.set_x(x_total)
    pdf.cell(col_pu, 8, "TOTAL :", align="R")
    pdf.cell(col_total, 8, f"{total_general:.2f} EUR", align="R")
    pdf.ln(15)

    # --- Conditions de paiement ---
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Conditions de paiement : A reception de facture", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "Moyen de paiement : Virement bancaire / Cheque / Especes", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
