"""
GP Entretien Extérieurs — Application de Gestion Interne
=========================================================
Point d'entrée Streamlit.
Thème clair/sombre, navigation, dashboard, recherche globale.

Lancement : python -m streamlit run app.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from database.db import init_db
from services import client_service, document_service, outil_service, event_service, invoice_service
from services import notion_service, pdf_service
from models.document import STATUTS as STATUTS_DOC
from models.outil import ETATS as ETATS_OUTIL, ETATS_ICONES
from models.event import STATUTS as STATUTS_EVENT, STATUTS_ICONES as STATUTS_EVENT_ICONES
from models.invoice import STATUTS as STATUTS_FACTURE, STATUTS_ICONES as STATUTS_FACTURE_ICONES
from modules import clients as mod_clients
from modules import documents as mod_documents
from modules import outils as mod_outils
from modules import agenda as mod_agenda
from utils.theme import (
    generer_css,
    html_stat_card,
    html_badge,
    html_section_header,
    html_empty_state,
    html_divider,
    html_mini_metric,
    html_result_count,
)


# ============================================================
# CONFIGURATION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="GP Entretien — Gestion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# Thème par défaut
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

mode = st.session_state["theme_mode"]

# Injection du CSS complet selon le thème actif
st.markdown(generer_css(mode), unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    # Branding
    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">🌿</div>
        <div class="name">GP Entretien Extérieurs</div>
        <div class="tagline">Gestion interne</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(html_divider(), unsafe_allow_html=True)

    # Toggle thème
    is_dark = st.toggle(
        "🌙 Mode sombre",
        value=(mode == "dark"),
        key="toggle_theme",
    )
    nouveau_mode = "dark" if is_dark else "light"
    if nouveau_mode != mode:
        st.session_state["theme_mode"] = nouveau_mode
        st.rerun()

    st.markdown(html_divider(), unsafe_allow_html=True)

    # Navigation
    pages = {
        "📊  Tableau de bord": "dashboard",
        "📅  Agenda":          "agenda",
        "👥  Clients":         "clients",
        "📄  Documents":       "documents",
        "🔧  Outils":         "outils",
        "🏢  Entreprise":      "entreprise_config",
        "⚙️  Notion":          "notion_config",
    }
    choix = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    page = pages[choix]

    st.markdown(html_divider(), unsafe_allow_html=True)

    # Recherche globale
    st.markdown("**🔍 Recherche globale**")
    terme = st.text_input(
        "Rechercher partout",
        placeholder="Nom, fichier, outil...",
        key="recherche_globale",
        label_visibility="collapsed",
    )

    if terme:
        res_c = client_service.recherche_globale(terme)
        res_d = document_service.recherche_globale(terme)
        res_o = outil_service.recherche_globale(terme)
        res_e = event_service.recherche_globale(terme)
        res_f = invoice_service.recherche_globale(terme)
        total = len(res_c) + len(res_d) + len(res_o) + len(res_e) + len(res_f)

        if total == 0:
            st.caption("Aucun résultat.")
        else:
            st.caption(f"{total} résultat(s)")
            if res_e:
                st.markdown("**Evenements**")
                for e in res_e:
                    st.write(f"📅 {e['titre']}")
            if res_c:
                st.markdown("**Clients**")
                for c in res_c:
                    st.write(f"👤 {c['nom']}")
            if res_d:
                st.markdown("**Documents**")
                for d in res_d:
                    st.write(f"📄 {d['nom_original']}")
            if res_o:
                st.markdown("**Outils**")
                for o in res_o:
                    st.write(f"🔧 {o['nom']}")
            if res_f:
                st.markdown("**Factures**")
                for f in res_f:
                    st.write(f"💰 {f['description']}")

    st.markdown(html_divider(), unsafe_allow_html=True)
    st.markdown('<div class="sidebar-version">v2.0 — Application locale</div>', unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

def afficher_dashboard():
    """Tableau de bord avec statistiques et résumés visuels."""
    st.markdown(html_section_header("📊", "Tableau de bord", "Vue d'ensemble de votre activité"), unsafe_allow_html=True)

    nb_clients = client_service.compter()
    nb_docs = document_service.compter()
    nb_outils = outil_service.compter()
    nb_events = event_service.compter()
    nb_factures = invoice_service.compter()

    # --- Cartes principales ---
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(html_stat_card("📅", nb_events, "Evenements"), unsafe_allow_html=True)
    with col2:
        st.markdown(html_stat_card("💰", nb_factures, "Factures"), unsafe_allow_html=True)
    with col3:
        st.markdown(html_stat_card("👥", nb_clients, "Clients"), unsafe_allow_html=True)
    with col4:
        st.markdown(html_stat_card("📄", nb_docs, "Documents"), unsafe_allow_html=True)
    with col5:
        st.markdown(html_stat_card("🔧", nb_outils, "Outils"), unsafe_allow_html=True)

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Prochains evenements ---
    st.markdown('<div class="sub-header">📅 Prochains evenements</div>', unsafe_allow_html=True)
    prochains = event_service.evenements_a_venir(5)
    if prochains:
        for ev in prochains:
            badge = html_badge(ev.statut, f"{ev.statut_icone} {ev.statut_label}")
            client_txt = f" · 👤 {ev.client_nom}" if ev.client_nom else ""
            heure = ev.date_debut[11:16] if len(ev.date_debut) > 10 else ""
            st.markdown(f"""
            <div class="entity-card">
                <div class="entity-title">📅 {ev.titre} {badge}</div>
                <div class="entity-field">🕐 {ev.date_debut[:10]} {heure}{client_txt}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(html_empty_state("📅", "Aucun evenement a venir"), unsafe_allow_html=True)

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Détails par catégorie ---
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown('<div class="sub-header">📅 Evenements par statut</div>', unsafe_allow_html=True)
        events_statut = event_service.compter_par_statut()
        if events_statut:
            html = ""
            for statut, count in events_statut.items():
                label = STATUTS_EVENT.get(statut, statut)
                ic = STATUTS_EVENT_ICONES.get(statut, "📅")
                html += html_mini_metric(ic, label, count)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(html_empty_state("📅", "Aucun evenement"), unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="sub-header">📄 Documents par statut</div>', unsafe_allow_html=True)
        docs_statut = document_service.compter_par_statut()
        if docs_statut:
            icones_statut = {"recu": "📥", "en_cours": "⏳", "envoye": "📤", "archive": "🗄️"}
            html = ""
            for statut, count in docs_statut.items():
                label = STATUTS_DOC.get(statut, statut)
                ic = icones_statut.get(statut, "📄")
                html += html_mini_metric(ic, label, count)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(html_empty_state("📄", "Aucun document enregistré"), unsafe_allow_html=True)

    with col_c:
        st.markdown('<div class="sub-header">🔧 Outils par état</div>', unsafe_allow_html=True)
        outils_etat = outil_service.compter_par_etat()
        if outils_etat:
            html = ""
            for etat, count in outils_etat.items():
                label = ETATS_OUTIL.get(etat, etat)
                ic = ETATS_ICONES.get(etat, "🔧")
                html += html_mini_metric(ic, label, count)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(html_empty_state("🔧", "Aucun outil enregistré"), unsafe_allow_html=True)

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Factures en attente ---
    st.markdown('<div class="sub-header">💰 Factures</div>', unsafe_allow_html=True)
    factures_statut = invoice_service.compter_par_statut()
    totaux = invoice_service.total_montant_par_statut()
    if factures_statut:
        html = ""
        for statut_key, label in STATUTS_FACTURE.items():
            count = factures_statut.get(statut_key, 0)
            montant = totaux.get(statut_key, 0.0)
            ic = STATUTS_FACTURE_ICONES.get(statut_key, "💰")
            html += html_mini_metric(ic, f"{label} ({count})", f"{montant:.2f} EUR")
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html_empty_state("💰", "Aucune facture"), unsafe_allow_html=True)

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Derniers clients ---
    st.markdown('<div class="sub-header">👥 Derniers clients</div>', unsafe_allow_html=True)
    derniers = client_service.lister_recents(5)
    if derniers:
        for c in derniers:
            tel = c.telephone or "—"
            email = c.email or "—"
            st.markdown(f"""
            <div class="entity-card">
                <div class="entity-title">👤 {c.nom}</div>
                <div class="entity-field">📞 {tel}  ·  ✉️ {email}  ·  📅 {c.date_creation}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(html_empty_state("👥", "Aucun client enregistré"), unsafe_allow_html=True)


# ============================================================
# CONFIGURATION ENTREPRISE (template facture)
# ============================================================

def afficher_config_entreprise():
    """Page de configuration des informations entreprise pour les factures."""
    st.markdown(
        html_section_header("🏢", "Informations Entreprise", "Ces informations apparaitront sur vos factures PDF"),
        unsafe_allow_html=True,
    )

    config = pdf_service.charger_config()

    with st.form("form_entreprise_config"):
        nom = st.text_input("Nom de l'entreprise *", value=config.get("nom", ""))

        col1, col2 = st.columns(2)
        with col1:
            adresse = st.text_input("Adresse", value=config.get("adresse", ""))
            code_postal = st.text_input("Code postal", value=config.get("code_postal", ""))
            ville = st.text_input("Ville", value=config.get("ville", ""))
        with col2:
            telephone = st.text_input("Telephone", value=config.get("telephone", ""))
            email = st.text_input("Email", value=config.get("email", ""))
            siret = st.text_input("SIRET", value=config.get("siret", ""))

        mention_legale = st.text_input(
            "Mention legale (pied de facture)",
            value=config.get("mention_legale", ""),
        )

        col_s, _ = st.columns([1, 5])
        with col_s:
            sauver = st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True)

    if sauver:
        pdf_service.sauvegarder_config({
            "nom": nom,
            "adresse": adresse,
            "code_postal": code_postal,
            "ville": ville,
            "telephone": telephone,
            "email": email,
            "siret": siret,
            "mention_legale": mention_legale,
        })
        st.success("Configuration entreprise sauvegardee.")

    st.markdown(html_divider(), unsafe_allow_html=True)

    # Apercu
    st.markdown('<div class="sub-header">📄 Apercu facture</div>', unsafe_allow_html=True)
    st.caption("Telechargez un apercu pour voir le rendu de votre facture.")
    from models.invoice import Invoice as InvoiceModel
    exemple = InvoiceModel(
        id=1,
        description="Tonte pelouse + taille haies",
        montant=150.00,
        statut="en_attente",
        client_nom="Client Exemple",
    )
    pdf_bytes = pdf_service.generer_facture_pdf(exemple)
    st.download_button(
        "📄 Telecharger l'apercu PDF",
        data=pdf_bytes,
        file_name="Apercu_Facture.pdf",
        mime="application/pdf",
        type="primary",
    )


# ============================================================
# CONFIGURATION NOTION
# ============================================================

def afficher_config_notion():
    """Page de configuration de l'integration Notion."""
    st.markdown(
        html_section_header("⚙️", "Integration Notion", "Synchronisez vos evenements avec Notion"),
        unsafe_allow_html=True,
    )

    config = notion_service.charger_config()

    st.markdown("""
    **Comment configurer l'integration Notion :**
    1. Creez une integration sur [notion.so/my-integrations](https://www.notion.so/my-integrations)
    2. Copiez la cle API (Internal Integration Secret)
    3. Creez une base de donnees Notion avec les proprietes : **Titre** (title), **Date** (date), **Client** (rich_text), **Statut** (select), **Type** (select)
    4. Partagez la base de donnees avec votre integration
    5. Copiez l'ID de la base (dans l'URL de la page)
    """)

    st.markdown(html_divider(), unsafe_allow_html=True)

    with st.form("form_notion_config"):
        api_key = st.text_input(
            "Cle API Notion",
            value=config.get("api_key", ""),
            type="password",
            placeholder="secret_...",
        )
        database_id = st.text_input(
            "ID de la base de donnees Notion",
            value=config.get("database_id", ""),
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        )
        active = st.checkbox("Activer la synchronisation", value=config.get("active", False))

        col_s, col_t, _ = st.columns([1, 1, 4])
        with col_s:
            sauver = st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True)
        with col_t:
            tester = st.form_submit_button("🔗 Tester la connexion", use_container_width=True)

    if sauver:
        notion_service.sauvegarder_config({
            "api_key": api_key,
            "database_id": database_id,
            "active": active,
        })
        st.success("Configuration sauvegardee.")

    if tester:
        if not api_key or not database_id:
            st.error("Veuillez renseigner la cle API et l'ID de la base.")
        else:
            ok, msg = notion_service.tester_connexion(api_key, database_id)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown(html_divider(), unsafe_allow_html=True)

    # Synchronisation manuelle
    st.markdown('<div class="sub-header">📤 Synchronisation manuelle</div>', unsafe_allow_html=True)

    if not notion_service.est_configure():
        st.info("Configurez et activez l'integration Notion pour pouvoir synchroniser.")
    else:
        st.caption("Exporte tous les evenements vers votre base Notion.")
        if st.button("📤 Synchroniser tous les evenements", type="primary"):
            events = event_service.lister()
            if not events:
                st.warning("Aucun evenement a synchroniser.")
            else:
                with st.spinner("Synchronisation en cours..."):
                    succes, erreurs, messages = notion_service.synchroniser_tous_les_events(events)
                st.success(f"{succes} evenement(s) synchronise(s).")
                if erreurs:
                    st.warning(f"{erreurs} erreur(s) :")
                    for m in messages:
                        st.caption(f"- {m}")


# ============================================================
# ROUTEUR
# ============================================================

if page == "dashboard":
    afficher_dashboard()
elif page == "agenda":
    mod_agenda.afficher_page()
elif page == "clients":
    mod_clients.afficher_page()
elif page == "documents":
    mod_documents.afficher_page()
elif page == "outils":
    mod_outils.afficher_page()
elif page == "entreprise_config":
    afficher_config_entreprise()
elif page == "notion_config":
    afficher_config_notion()
