"""
Système de thème clair / sombre.
Génère le CSS complet de l'application selon le mode choisi.
Toutes les couleurs et styles sont centralisés ici.
"""

# ============================================================
# PALETTES DE COULEURS
# ============================================================

PALETTE = {
    "light": {
        "bg_main":          "#F4F6F8",
        "bg_sidebar":       "#FFFFFF",
        "bg_card":          "#FFFFFF",
        "bg_card_hover":    "#F0F4F0",
        "bg_input":         "#FFFFFF",
        "bg_header":        "#FFFFFF",
        "border":           "#D0D5DD",
        "border_accent":    "#2E7D32",
        "text_primary":     "#111827",
        "text_secondary":   "#374151",
        "text_muted":       "#6B7280",
        "accent":           "#1B6B20",
        "accent_light":     "#DEF2DF",
        "accent_hover":     "#145216",
        "danger":           "#B91C1C",
        "danger_light":     "#FEE2E2",
        "warning":          "#B45309",
        "warning_light":    "#FEF3C7",
        "info":             "#1D4ED8",
        "info_light":       "#DBEAFE",
        "success":          "#166534",
        "success_light":    "#DCFCE7",
        "shadow":           "rgba(0,0,0,0.08)",
        "shadow_hover":     "rgba(0,0,0,0.16)",
        "gradient_start":   "#FFFFFF",
        "gradient_end":     "#E8F5E9",
    },
    "dark": {
        "bg_main":          "#0E1117",
        "bg_sidebar":       "#161B22",
        "bg_card":          "#1A1F2B",
        "bg_card_hover":    "#242B38",
        "bg_input":         "#1A1F2B",
        "bg_header":        "#1E2530",
        "border":           "#2D333B",
        "border_accent":    "#4CAF50",
        "text_primary":     "#E6EDF3",
        "text_secondary":   "#ADBAC7",
        "text_muted":       "#768390",
        "accent":           "#4CAF50",
        "accent_light":     "#1A2E1A",
        "accent_hover":     "#66BB6A",
        "danger":           "#EF5350",
        "danger_light":     "#2E1A1A",
        "warning":          "#FFB74D",
        "warning_light":    "#2E2A1A",
        "info":             "#42A5F5",
        "info_light":       "#1A2230",
        "success":          "#4CAF50",
        "success_light":    "#1A2E1A",
        "shadow":           "rgba(0,0,0,0.3)",
        "shadow_hover":     "rgba(0,0,0,0.5)",
        "gradient_start":   "#161B22",
        "gradient_end":     "#1A2E1A",
    },
}


def get_colors(mode: str) -> dict:
    """Retourne la palette de couleurs pour le mode donné."""
    return PALETTE.get(mode, PALETTE["light"])


# ============================================================
# GÉNÉRATION CSS
# ============================================================

def generer_css(mode: str) -> str:
    """Génère le CSS complet de l'application pour le mode choisi."""
    c = get_colors(mode)
    return f"""
<style>
    /* ===== RESET & BASE ===== */
    .stApp {{
        background-color: {c['bg_main']};
        color: {c['text_primary']};
    }}

    /* Header Streamlit (barre du haut) */
    header[data-testid="stHeader"] {{
        background-color: {c['bg_header']};
        border-bottom: 1px solid {c['border']};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {c['bg_sidebar']};
        border-right: 1px solid {c['border']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {c['text_primary']} !important;
    }}

    /* Labels des inputs */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stFileUploader label, .stRadio label {{
        color: {c['text_primary']} !important;
        font-weight: 500;
    }}
    /* Texte dans les inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        color: {c['text_primary']} !important;
        background-color: {c['bg_input']} !important;
        border-color: {c['border']} !important;
    }}
    /* Texte st.write / st.markdown */
    .stMarkdown, .stMarkdown p {{
        color: {c['text_primary']};
    }}
    /* Expander header text */
    .streamlit-expanderHeader p {{
        color: {c['text_primary']} !important;
        font-weight: 500;
    }}

    /* ===== CARTES STATISTIQUES ===== */
    .stat-card {{
        background: linear-gradient(135deg, {c['gradient_start']}, {c['gradient_end']});
        border: 1px solid {c['border']};
        border-left: 5px solid {c['border_accent']};
        border-radius: 12px;
        padding: 1.5rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px {c['shadow']}, 0 1px 3px {c['shadow']};
        transition: all 0.25s ease;
    }}
    .stat-card:hover {{
        box-shadow: 0 6px 20px {c['shadow_hover']};
        transform: translateY(-2px);
    }}
    .stat-icon {{
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .stat-number {{
        font-size: 2.4rem;
        font-weight: 800;
        color: {c['accent']};
        line-height: 1.1;
    }}
    .stat-label {{
        font-size: 0.9rem;
        color: {c['text_secondary']};
        margin-top: 0.3rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ===== CARTES ENTITÉS (clients, docs, outils) ===== */
    .entity-card {{
        background: {c['bg_card']};
        border: 1px solid {c['border']};
        border-left: 4px solid {c['border_accent']};
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px {c['shadow']}, 0 1px 2px {c['shadow']};
        transition: all 0.2s ease;
    }}
    .entity-card:hover {{
        border-color: {c['border_accent']};
        box-shadow: 0 4px 16px {c['shadow_hover']};
    }}
    .entity-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {c['text_primary']};
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .entity-field {{
        font-size: 0.9rem;
        color: {c['text_secondary']};
        margin-bottom: 0.3rem;
        line-height: 1.6;
    }}
    .entity-field strong {{
        color: {c['text_primary']};
        font-weight: 600;
    }}

    /* ===== BADGES ===== */
    .badge {{
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}
    .badge-recu       {{ background: {c['info_light']};    color: {c['info']};    border: 1px solid {c['info']}33; }}
    .badge-en_cours   {{ background: {c['warning_light']}; color: {c['warning']}; border: 1px solid {c['warning']}33; }}
    .badge-envoye     {{ background: {c['success_light']}; color: {c['success']}; border: 1px solid {c['success']}33; }}
    .badge-archive    {{ background: {c['bg_header']};     color: {c['text_muted']}; border: 1px solid {c['border']}; }}
    .badge-disponible {{ background: {c['success_light']}; color: {c['success']}; border: 1px solid {c['success']}33; }}
    .badge-utilise    {{ background: {c['info_light']};    color: {c['info']};    border: 1px solid {c['info']}33; }}
    .badge-maintenance{{ background: {c['warning_light']}; color: {c['warning']}; border: 1px solid {c['warning']}33; }}

    /* Badges evenements */
    .badge-planifie   {{ background: {c['info_light']};    color: {c['info']};    border: 1px solid {c['info']}33; }}
    .badge-termine    {{ background: {c['success_light']}; color: {c['success']}; border: 1px solid {c['success']}33; }}
    .badge-annule     {{ background: {c['danger_light']};  color: {c['danger']};  border: 1px solid {c['danger']}33; }}

    /* Badges factures */
    .badge-brouillon  {{ background: {c['bg_header']};     color: {c['text_muted']}; border: 1px solid {c['border']}; }}
    .badge-en_attente {{ background: {c['warning_light']}; color: {c['warning']}; border: 1px solid {c['warning']}33; }}
    .badge-paye       {{ background: {c['success_light']}; color: {c['success']}; border: 1px solid {c['success']}33; }}

    /* ===== EN-TÊTES DE SECTION ===== */
    .section-header {{
        font-size: 1.6rem;
        font-weight: 800;
        color: {c['accent']};
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}
    .section-subtitle {{
        font-size: 0.95rem;
        color: {c['text_muted']};
        margin-bottom: 1.5rem;
    }}
    .sub-header {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {c['text_primary']};
        margin: 1.2rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid {c['border']};
    }}

    /* ===== SÉPARATEUR ===== */
    .divider {{
        border: none;
        border-top: 1px solid {c['border']};
        margin: 1.5rem 0;
    }}

    /* ===== COMPTEUR DE RÉSULTATS ===== */
    .result-count {{
        display: inline-block;
        background: {c['accent_light']};
        color: {c['accent']};
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }}

    /* ===== INFO VIDE ===== */
    .empty-state {{
        text-align: center;
        padding: 3rem 1rem;
        color: {c['text_muted']};
    }}
    .empty-state .icon {{
        font-size: 3rem;
        margin-bottom: 0.8rem;
    }}
    .empty-state .message {{
        font-size: 1rem;
    }}

    /* ===== SIDEBAR BRANDING ===== */
    .sidebar-brand {{
        text-align: center;
        padding: 0.5rem 0 1rem 0;
    }}
    .sidebar-brand .logo {{
        font-size: 2.2rem;
    }}
    .sidebar-brand .name {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {c['accent']} !important;
        margin-top: 0.2rem;
    }}
    .sidebar-brand .tagline {{
        font-size: 0.75rem;
        color: {c['text_muted']} !important;
    }}
    .sidebar-version {{
        text-align: center;
        font-size: 0.72rem;
        color: {c['text_muted']} !important;
        padding: 0.5rem 0;
    }}

    /* ===== EXPANDER OVERRIDE ===== */
    .streamlit-expanderHeader {{
        background: {c['bg_card']} !important;
        border-radius: 8px !important;
    }}

    /* ===== MÉTRIQUE MINI (pour dashboard détails) ===== */
    .mini-metric {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid {c['border']};
    }}
    .mini-metric:last-child {{
        border-bottom: none;
    }}
    .mini-metric .mm-icon {{
        font-size: 1.3rem;
    }}
    .mini-metric .mm-label {{
        flex: 1;
        font-size: 0.9rem;
        color: {c['text_secondary']};
    }}
    .mini-metric .mm-value {{
        font-size: 1rem;
        font-weight: 700;
        color: {c['text_primary']};
    }}
</style>
"""


# ============================================================
# COMPOSANTS HTML RÉUTILISABLES
# ============================================================

def html_stat_card(icone: str, nombre: int | str, label: str) -> str:
    """Génère le HTML d'une carte de statistique pour le dashboard."""
    return f"""
    <div class="stat-card">
        <div class="stat-icon">{icone}</div>
        <div class="stat-number">{nombre}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


def html_badge(cle: str, label: str) -> str:
    """Génère un badge HTML coloré selon la clé (statut ou état)."""
    return f'<span class="badge badge-{cle}">{label}</span>'


def html_section_header(icone: str, titre: str, sous_titre: str = "") -> str:
    """Génère un en-tête de section avec icône."""
    html = f'<div class="section-header">{icone} {titre}</div>'
    if sous_titre:
        html += f'<div class="section-subtitle">{sous_titre}</div>'
    return html


def html_empty_state(icone: str, message: str) -> str:
    """Génère un état vide centré avec icône."""
    return f"""
    <div class="empty-state">
        <div class="icon">{icone}</div>
        <div class="message">{message}</div>
    </div>
    """


def html_result_count(count: int, label: str = "résultat(s)") -> str:
    """Génère un compteur de résultats stylisé."""
    return f'<span class="result-count">{count} {label}</span>'


def html_divider() -> str:
    """Génère un séparateur horizontal."""
    return '<hr class="divider">'


def html_mini_metric(icone: str, label: str, valeur: str | int) -> str:
    """Génère une ligne de métrique compacte pour le dashboard."""
    return f"""
    <div class="mini-metric">
        <span class="mm-icon">{icone}</span>
        <span class="mm-label">{label}</span>
        <span class="mm-value">{valeur}</span>
    </div>
    """
