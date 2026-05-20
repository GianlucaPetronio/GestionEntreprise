"""
Module UI Streamlit : Agenda / Planning.
Interface avec vue calendrier (jour/semaine), gestion des evenements,
assignation d'outils, suivi de statut et facturation liee.
Logique metier deleguee a event_service et invoice_service.
"""

import streamlit as st
from datetime import datetime, timedelta, date

from models.event import Event, STATUTS, STATUTS_ICONES, TYPES_TRAVAIL
from models.invoice import Invoice, STATUTS as STATUTS_FACTURE, STATUTS_ICONES as STATUTS_FACTURE_ICONES
from services import event_service, invoice_service, client_service, outil_service, notion_service, pdf_service
from utils.theme import (
    html_section_header,
    html_empty_state,
    html_result_count,
    html_badge,
    html_divider,
)


# ============================================================
# POINT D'ENTREE
# ============================================================

def afficher_page():
    """Point d'entree : page Agenda / Planning."""
    st.markdown(
        html_section_header("📅", "Agenda / Planning", "Planification et suivi de vos interventions"),
        unsafe_allow_html=True,
    )

    # Onglets principaux
    tab_agenda, tab_factures = st.tabs(["📅 Agenda", "💰 Factures"])

    with tab_agenda:
        _afficher_section_agenda()

    with tab_factures:
        _afficher_section_factures()


# ============================================================
# SECTION AGENDA
# ============================================================

def _afficher_section_agenda():
    """Section principale de l'agenda avec filtres et routage."""
    # --- Barre d'actions ---
    col_vue, col_filtre_client, col_btn = st.columns([1, 1, 1])

    with col_vue:
        vue = st.selectbox(
            "Vue",
            ["Liste", "Semaine", "Jour"],
            key="agenda_vue",
            label_visibility="collapsed",
        )

    with col_filtre_client:
        clients = client_service.lister_pour_selection()
        options_clients = [{"id": None, "nom": "Tous les clients"}] + clients
        choix_client = st.selectbox(
            "Client",
            options_clients,
            format_func=lambda x: x["nom"],
            key="agenda_filtre_client",
            label_visibility="collapsed",
        )
        filtre_client_id = choix_client["id"]

    with col_btn:
        if st.button("➕ Nouvel evenement", use_container_width=True, type="primary"):
            st.session_state["mode_agenda"] = "ajout"

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Routage ---
    mode = st.session_state.get("mode_agenda")
    if mode == "ajout":
        _formulaire_ajout_event()
    elif mode == "modification":
        _formulaire_modification_event(st.session_state.get("event_edit_id"))
    elif mode == "detail":
        _afficher_detail_event(st.session_state.get("event_detail_id"))
    elif mode == "creer_facture":
        _formulaire_creer_facture_depuis_event(st.session_state.get("event_facture_id"))
    else:
        if vue == "Semaine":
            _afficher_vue_semaine(filtre_client_id)
        elif vue == "Jour":
            _afficher_vue_jour(filtre_client_id)
        else:
            _afficher_vue_liste(filtre_client_id)


# ============================================================
# VUES CALENDRIER
# ============================================================

def _afficher_vue_liste(filtre_client_id: int | None):
    """Vue liste de tous les evenements."""
    col_rech, col_stat = st.columns([2, 1])
    with col_rech:
        recherche = st.text_input(
            "Rechercher",
            placeholder="Titre, description...",
            key="rech_event",
            label_visibility="collapsed",
        )
    with col_stat:
        opts_statut = ["Tous les statuts"] + list(STATUTS.values())
        choix_statut = st.selectbox("Statut", opts_statut, key="filtre_statut_event", label_visibility="collapsed")
        filtre_statut = ""
        for cle, val in STATUTS.items():
            if val == choix_statut:
                filtre_statut = cle
                break

    events = event_service.lister(recherche, filtre_statut, filtre_client_id)

    if not events:
        icone = "🔍" if (recherche or filtre_statut) else "📅"
        msg = "Aucun evenement trouve." if (recherche or filtre_statut) else "Aucun evenement planifie. Creez votre premier evenement."
        st.markdown(html_empty_state(icone, msg), unsafe_allow_html=True)
        return

    st.markdown(html_result_count(len(events), "evenement(s)"), unsafe_allow_html=True)

    for ev in events:
        _afficher_carte_event(ev)


def _afficher_vue_semaine(filtre_client_id: int | None):
    """Vue calendrier semaine."""
    # Navigation semaine
    if "agenda_semaine_offset" not in st.session_state:
        st.session_state["agenda_semaine_offset"] = 0

    col_prev, col_titre, col_next, col_today = st.columns([1, 4, 1, 1])

    with col_prev:
        if st.button("◀ Prec.", key="sem_prev", use_container_width=True):
            st.session_state["agenda_semaine_offset"] -= 1
            st.rerun()
    with col_next:
        if st.button("Suiv. ▶", key="sem_next", use_container_width=True):
            st.session_state["agenda_semaine_offset"] += 1
            st.rerun()
    with col_today:
        if st.button("Aujourd'hui", key="sem_today", use_container_width=True):
            st.session_state["agenda_semaine_offset"] = 0
            st.rerun()

    offset = st.session_state["agenda_semaine_offset"]
    today = date.today()
    lundi = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    dimanche = lundi + timedelta(days=6)

    with col_titre:
        st.markdown(
            f'<div class="sub-header">Semaine du {lundi.strftime("%d/%m/%Y")} au {dimanche.strftime("%d/%m/%Y")}</div>',
            unsafe_allow_html=True,
        )

    # Charger les evenements de la semaine
    date_start = lundi.strftime("%Y-%m-%d")
    date_end = (dimanche + timedelta(days=1)).strftime("%Y-%m-%d")
    events = event_service.lister_par_periode(date_start, date_end, filtre_client_id)

    # Grouper par jour
    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    for i in range(7):
        jour_date = lundi + timedelta(days=i)
        jour_str = jour_date.strftime("%Y-%m-%d")
        jour_events = [e for e in events if e.date_debut.startswith(jour_str)]

        is_today = jour_date == today
        label_jour = f"**{jours_semaine[i]} {jour_date.strftime('%d/%m')}**"
        if is_today:
            label_jour += " (aujourd'hui)"

        with st.expander(f"{label_jour} — {len(jour_events)} evenement(s)", expanded=is_today):
            if jour_events:
                for ev in jour_events:
                    _afficher_carte_event(ev, compact=True)
            else:
                st.caption("Aucun evenement.")


def _afficher_vue_jour(filtre_client_id: int | None):
    """Vue calendrier jour."""
    if "agenda_jour_offset" not in st.session_state:
        st.session_state["agenda_jour_offset"] = 0

    col_prev, col_titre, col_next, col_today = st.columns([1, 4, 1, 1])

    with col_prev:
        if st.button("◀ Prec.", key="jour_prev", use_container_width=True):
            st.session_state["agenda_jour_offset"] -= 1
            st.rerun()
    with col_next:
        if st.button("Suiv. ▶", key="jour_next", use_container_width=True):
            st.session_state["agenda_jour_offset"] += 1
            st.rerun()
    with col_today:
        if st.button("Aujourd'hui", key="jour_today", use_container_width=True):
            st.session_state["agenda_jour_offset"] = 0
            st.rerun()

    offset = st.session_state["agenda_jour_offset"]
    jour = date.today() + timedelta(days=offset)

    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    nom_jour = jours_semaine[jour.weekday()]

    with col_titre:
        st.markdown(
            f'<div class="sub-header">{nom_jour} {jour.strftime("%d/%m/%Y")}</div>',
            unsafe_allow_html=True,
        )

    date_start = jour.strftime("%Y-%m-%d")
    date_end = (jour + timedelta(days=1)).strftime("%Y-%m-%d")
    events = event_service.lister_par_periode(date_start, date_end, filtre_client_id)

    if not events:
        st.markdown(html_empty_state("📅", "Aucun evenement ce jour."), unsafe_allow_html=True)
        return

    st.markdown(html_result_count(len(events), "evenement(s)"), unsafe_allow_html=True)

    for ev in events:
        _afficher_carte_event(ev)


# ============================================================
# CARTE EVENEMENT
# ============================================================

def _afficher_carte_event(ev: Event, compact: bool = False):
    """Affiche une carte d'evenement avec boutons d'actions."""
    badge_statut = html_badge(ev.statut, f"{ev.statut_icone} {ev.statut_label}")
    type_html = f' | {ev.type_label}' if ev.type_travail else ""
    client_html = f'<div class="entity-field">👤 <strong>Client :</strong> {ev.client_nom}</div>' if ev.client_nom else ""
    desc_html = ""
    if not compact and ev.description:
        desc_text = ev.description.replace("\n", "<br>")
        desc_html = f'<div class="entity-field">📝 {desc_text}</div>'

    # Extraire les heures pour affichage
    heure_debut = ev.date_debut[11:16] if len(ev.date_debut) > 10 else ""
    heure_fin = ev.date_fin[11:16] if len(ev.date_fin) > 10 else ""
    horaire = f"{heure_debut} - {heure_fin}" if heure_debut and heure_fin else ev.date_debut

    card_html = (
        '<div class="entity-card">'
        f'<div class="entity-title">📅 {ev.titre} {badge_statut}</div>'
        f'<div class="entity-field">🕐 {horaire}{type_html}</div>'
        f'{client_html}'
        f'{desc_html}'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Boutons d'action
    col_v, col_m, col_f, col_s, _ = st.columns([1, 1, 1, 1, 4])
    with col_v:
        if st.button("👁 Detail", key=f"voir_e_{ev.id}", use_container_width=True):
            st.session_state["mode_agenda"] = "detail"
            st.session_state["event_detail_id"] = ev.id
            st.rerun()
    with col_m:
        if st.button("✏️ Modifier", key=f"mod_e_{ev.id}", use_container_width=True):
            st.session_state["mode_agenda"] = "modification"
            st.session_state["event_edit_id"] = ev.id
            st.rerun()
    with col_f:
        if st.button("💰 Facturer", key=f"fac_e_{ev.id}", use_container_width=True):
            st.session_state["mode_agenda"] = "creer_facture"
            st.session_state["event_facture_id"] = ev.id
            st.rerun()
    with col_s:
        if st.button("🗑️", key=f"sup_e_{ev.id}", use_container_width=True):
            st.session_state["confirm_sup_event"] = ev.id
            st.rerun()

    # Confirmation suppression
    if st.session_state.get("confirm_sup_event") == ev.id:
        st.warning(f"Confirmer la suppression de **{ev.titre}** ?")
        col_y, col_n, _ = st.columns([1, 1, 6])
        with col_y:
            if st.button("✅ Confirmer", key=f"oui_e_{ev.id}", type="primary"):
                event_service.supprimer(ev.id)
                st.session_state.pop("confirm_sup_event", None)
                st.success("Evenement supprime.")
                st.rerun()
        with col_n:
            if st.button("❌ Annuler", key=f"non_e_{ev.id}"):
                st.session_state.pop("confirm_sup_event", None)
                st.rerun()

    if not compact:
        st.write("")


# ============================================================
# DETAIL EVENEMENT
# ============================================================

def _afficher_detail_event(event_id: int):
    """Affiche le detail complet d'un evenement."""
    ev = event_service.obtenir(event_id)
    if not ev:
        st.error("Evenement introuvable.")
        st.session_state["mode_agenda"] = None
        return

    if st.button("← Retour a l'agenda", key="retour_agenda"):
        st.session_state["mode_agenda"] = None
        st.rerun()

    st.markdown(f'<div class="sub-header">📅 {ev.titre}</div>', unsafe_allow_html=True)

    badge_statut = html_badge(ev.statut, f"{ev.statut_icone} {ev.statut_label}")
    st.markdown(badge_statut, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Date debut :** {ev.date_debut}")
        st.markdown(f"**Date fin :** {ev.date_fin}")
        if ev.client_nom:
            st.markdown(f"**Client :** {ev.client_nom}")
    with col2:
        if ev.type_travail:
            st.markdown(f"**Type :** {ev.type_label}")
        if ev.outils_noms:
            st.markdown(f"**Outils :** {', '.join(ev.outils_noms)}")

    if ev.description:
        st.markdown(f"**Description :** {ev.description}")
    if ev.notes:
        st.markdown(f"**Notes d'intervention :** {ev.notes}")

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Factures liees ---
    st.markdown('<div class="sub-header">💰 Factures liees</div>', unsafe_allow_html=True)
    factures = invoice_service.lister_pour_event(event_id)

    if factures:
        for fac in factures:
            badge_fac = html_badge(fac.statut, f"{fac.statut_icone} {fac.statut_label}")
            fac_desc = fac.description.replace("\n", "<br>") if fac.description else ""
            fac_card = (
                '<div class="entity-card">'
                f'<div class="entity-title">💰 Facture #{fac.id} {badge_fac}</div>'
                f'<div class="entity-field">📝 {fac_desc}</div>'
                f'<div class="entity-field">💶 <strong>{fac.montant_formate}</strong></div>'
                '</div>'
            )
            st.markdown(fac_card, unsafe_allow_html=True)
            pdf_bytes = pdf_service.generer_facture_pdf(fac)
            st.download_button(
                "📄 Telecharger PDF",
                data=pdf_bytes,
                file_name=f"Facture_FAC-{fac.id:04d}.pdf",
                mime="application/pdf",
                key=f"pdf_detail_f_{fac.id}",
            )
    else:
        st.caption("Aucune facture liee.")

    col_fac, col_notion, _ = st.columns([2, 2, 4])
    with col_fac:
        if st.button("➕ Creer une facture", key="creer_fac_detail", type="primary", use_container_width=True):
            st.session_state["mode_agenda"] = "creer_facture"
            st.session_state["event_facture_id"] = event_id
            st.rerun()
    with col_notion:
        if notion_service.est_configure():
            if st.button("📤 Sync Notion", key="sync_notion_detail", use_container_width=True):
                ok, msg = notion_service.synchroniser_event(ev)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# ============================================================
# FORMULAIRES EVENEMENTS
# ============================================================

def _formulaire_ajout_event():
    """Formulaire de creation d'un evenement."""
    st.markdown('<div class="sub-header">➕ Nouvel evenement</div>', unsafe_allow_html=True)

    clients = client_service.lister_pour_selection()
    outils = outil_service.lister()

    with st.form("form_ajout_event"):
        titre = st.text_input("Titre *", placeholder="Ex : Tonte pelouse M. Dupont")
        description = st.text_area("Description", placeholder="Details de l'intervention...")

        col1, col2 = st.columns(2)
        with col1:
            d_debut = st.date_input("Date debut *", value=date.today(), key="add_date_debut")
            h_debut = st.time_input("Heure debut", value=datetime.now().replace(hour=8, minute=0).time(), key="add_h_debut")
        with col2:
            d_fin = st.date_input("Date fin *", value=date.today(), key="add_date_fin")
            h_fin = st.time_input("Heure fin", value=datetime.now().replace(hour=12, minute=0).time(), key="add_h_fin")

        col3, col4 = st.columns(2)
        with col3:
            options_clients = [{"id": None, "nom": "— Aucun client —"}] + clients
            choix_client = st.selectbox(
                "Client",
                options_clients,
                format_func=lambda x: x["nom"],
                key="add_event_client",
            )
        with col4:
            type_travail = st.selectbox(
                "Type de travail",
                [""] + list(TYPES_TRAVAIL.keys()),
                format_func=lambda x: TYPES_TRAVAIL.get(x, "— Aucun —"),
                key="add_event_type",
            )

        # Selection multi-outils
        if outils:
            outils_options = {o.id: o.nom for o in outils}
            outils_selectionnes = st.multiselect(
                "Outils utilises",
                options=list(outils_options.keys()),
                format_func=lambda x: outils_options[x],
                key="add_event_outils",
            )
        else:
            outils_selectionnes = []
            st.caption("Aucun outil enregistre.")

        statut = st.selectbox(
            "Statut",
            list(STATUTS.keys()),
            format_func=lambda x: f"{STATUTS_ICONES.get(x, '')} {STATUTS[x]}",
            key="add_event_statut",
        )

        notes = st.text_area("Notes d'intervention", placeholder="Observations, consignes...", key="add_event_notes")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        date_debut_str = f"{d_debut.strftime('%Y-%m-%d')} {h_debut.strftime('%H:%M')}"
        date_fin_str = f"{d_fin.strftime('%Y-%m-%d')} {h_fin.strftime('%H:%M')}"

        event = Event(
            titre=titre,
            description=description,
            date_debut=date_debut_str,
            date_fin=date_fin_str,
            client_id=choix_client["id"],
            type_travail=type_travail,
            statut=statut,
            notes=notes,
        )
        erreurs = event.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            event_id = event_service.creer(event)
            if outils_selectionnes:
                event_service.associer_outils(event_id, outils_selectionnes)
            st.session_state["mode_agenda"] = None
            st.success(f"Evenement « {titre} » cree.")
            st.rerun()

    if annuler:
        st.session_state["mode_agenda"] = None
        st.rerun()


def _formulaire_modification_event(event_id: int):
    """Formulaire de modification d'un evenement."""
    ev = event_service.obtenir(event_id)
    if not ev:
        st.error("Evenement introuvable.")
        st.session_state["mode_agenda"] = None
        return

    st.markdown(f'<div class="sub-header">✏️ Modifier : {ev.titre}</div>', unsafe_allow_html=True)

    clients = client_service.lister_pour_selection()
    outils = outil_service.lister()
    outils_actuels = event_service.obtenir_outils_ids(event_id)

    # Parser les dates existantes
    try:
        dt_debut = datetime.strptime(ev.date_debut, "%Y-%m-%d %H:%M")
    except ValueError:
        dt_debut = datetime.now().replace(hour=8, minute=0)
    try:
        dt_fin = datetime.strptime(ev.date_fin, "%Y-%m-%d %H:%M")
    except ValueError:
        dt_fin = datetime.now().replace(hour=12, minute=0)

    with st.form("form_modif_event"):
        titre = st.text_input("Titre *", value=ev.titre)
        description = st.text_area("Description", value=ev.description or "")

        col1, col2 = st.columns(2)
        with col1:
            d_debut = st.date_input("Date debut *", value=dt_debut.date(), key="mod_date_debut")
            h_debut = st.time_input("Heure debut", value=dt_debut.time(), key="mod_h_debut")
        with col2:
            d_fin = st.date_input("Date fin *", value=dt_fin.date(), key="mod_date_fin")
            h_fin = st.time_input("Heure fin", value=dt_fin.time(), key="mod_h_fin")

        col3, col4 = st.columns(2)
        with col3:
            options_clients = [{"id": None, "nom": "— Aucun client —"}] + clients
            idx_client = 0
            for i, c in enumerate(options_clients):
                if c["id"] == ev.client_id:
                    idx_client = i
                    break
            choix_client = st.selectbox(
                "Client",
                options_clients,
                index=idx_client,
                format_func=lambda x: x["nom"],
                key="mod_event_client",
            )
        with col4:
            types_keys = [""] + list(TYPES_TRAVAIL.keys())
            idx_type = 0
            if ev.type_travail in types_keys:
                idx_type = types_keys.index(ev.type_travail)
            type_travail = st.selectbox(
                "Type de travail",
                types_keys,
                index=idx_type,
                format_func=lambda x: TYPES_TRAVAIL.get(x, "— Aucun —"),
                key="mod_event_type",
            )

        if outils:
            outils_options = {o.id: o.nom for o in outils}
            outils_selectionnes = st.multiselect(
                "Outils utilises",
                options=list(outils_options.keys()),
                default=[oid for oid in outils_actuels if oid in outils_options],
                format_func=lambda x: outils_options[x],
                key="mod_event_outils",
            )
        else:
            outils_selectionnes = []

        statuts_keys = list(STATUTS.keys())
        idx_statut = statuts_keys.index(ev.statut) if ev.statut in statuts_keys else 0
        statut = st.selectbox(
            "Statut",
            statuts_keys,
            index=idx_statut,
            format_func=lambda x: f"{STATUTS_ICONES.get(x, '')} {STATUTS[x]}",
            key="mod_event_statut",
        )

        notes = st.text_area("Notes d'intervention", value=ev.notes or "", key="mod_event_notes")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        date_debut_str = f"{d_debut.strftime('%Y-%m-%d')} {h_debut.strftime('%H:%M')}"
        date_fin_str = f"{d_fin.strftime('%Y-%m-%d')} {h_fin.strftime('%H:%M')}"

        modifie = Event(
            id=event_id,
            titre=titre,
            description=description,
            date_debut=date_debut_str,
            date_fin=date_fin_str,
            client_id=choix_client["id"],
            type_travail=type_travail,
            statut=statut,
            notes=notes,
        )
        erreurs = modifie.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            event_service.modifier(modifie)
            event_service.associer_outils(event_id, outils_selectionnes)
            st.session_state["mode_agenda"] = None
            st.success(f"Evenement « {titre} » modifie.")
            st.rerun()

    if annuler:
        st.session_state["mode_agenda"] = None
        st.rerun()


# ============================================================
# FACTURE DEPUIS EVENEMENT
# ============================================================

def _formulaire_creer_facture_depuis_event(event_id: int):
    """Formulaire de creation d'une facture pre-remplie depuis un evenement."""
    ev = event_service.obtenir(event_id)
    if not ev:
        st.error("Evenement introuvable.")
        st.session_state["mode_agenda"] = None
        return

    st.markdown(f'<div class="sub-header">💰 Creer une facture pour : {ev.titre}</div>', unsafe_allow_html=True)

    with st.form("form_creer_facture_event"):
        description = st.text_area(
            "Description *",
            value=f"{ev.titre} — {ev.date_debut[:10]}",
        )
        montant = st.number_input("Montant (EUR) *", min_value=0.0, step=10.0, format="%.2f")
        statut = st.selectbox(
            "Statut",
            list(STATUTS_FACTURE.keys()),
            format_func=lambda x: f"{STATUTS_FACTURE_ICONES.get(x, '')} {STATUTS_FACTURE[x]}",
        )

        st.caption(f"Client : **{ev.client_nom or '— Aucun —'}**")
        st.caption(f"Evenement lie : **{ev.titre}**")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Creer la facture", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        facture = Invoice(
            event_id=event_id,
            client_id=ev.client_id,
            description=description,
            montant=montant,
            statut=statut,
        )
        erreurs = facture.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            invoice_service.creer(facture)
            st.session_state["mode_agenda"] = "detail"
            st.session_state["event_detail_id"] = event_id
            st.success("Facture creee avec succes.")
            st.rerun()

    if annuler:
        st.session_state["mode_agenda"] = None
        st.rerun()


# ============================================================
# SECTION FACTURES
# ============================================================

def _afficher_section_factures():
    """Onglet de gestion des factures."""
    col_rech, col_stat, col_btn = st.columns([2, 1, 1])
    with col_rech:
        recherche = st.text_input(
            "Rechercher",
            placeholder="Description, client...",
            key="rech_facture",
            label_visibility="collapsed",
        )
    with col_stat:
        opts_statut = ["Tous les statuts"] + list(STATUTS_FACTURE.values())
        choix_statut = st.selectbox("Statut", opts_statut, key="filtre_statut_facture")
        filtre_statut = ""
        for cle, val in STATUTS_FACTURE.items():
            if val == choix_statut:
                filtre_statut = cle
                break
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Nouvelle facture", use_container_width=True, type="primary"):
            st.session_state["mode_facture"] = "ajout"

    st.markdown(html_divider(), unsafe_allow_html=True)

    mode_fac = st.session_state.get("mode_facture")
    if mode_fac == "ajout":
        _formulaire_ajout_facture()
    elif mode_fac == "modification":
        _formulaire_modification_facture(st.session_state.get("facture_edit_id"))
    else:
        _afficher_liste_factures(recherche, filtre_statut)


def _afficher_liste_factures(recherche: str, filtre_statut: str):
    """Affiche la liste des factures."""
    # Totaux en haut
    totaux = invoice_service.total_montant_par_statut()
    if totaux:
        cols = st.columns(len(STATUTS_FACTURE))
        for i, (cle, label) in enumerate(STATUTS_FACTURE.items()):
            with cols[i]:
                montant = totaux.get(cle, 0.0)
                icone = STATUTS_FACTURE_ICONES.get(cle, "")
                st.metric(f"{icone} {label}", f"{montant:.2f} EUR")

        st.markdown(html_divider(), unsafe_allow_html=True)

    factures = invoice_service.lister(recherche, filtre_statut)

    if not factures:
        st.markdown(html_empty_state("💰", "Aucune facture."), unsafe_allow_html=True)
        return

    st.markdown(html_result_count(len(factures), "facture(s)"), unsafe_allow_html=True)

    for fac in factures:
        badge = html_badge(fac.statut, f"{fac.statut_icone} {fac.statut_label}")
        client_html = f'<div class="entity-field">👤 {fac.client_nom}</div>' if fac.client_nom else ""
        event_html = f'<div class="entity-field">📅 Evenement : {fac.event_titre}</div>' if fac.event_titre else ""

        fac_desc = fac.description.replace("\n", "<br>") if fac.description else ""
        fac_card = (
            '<div class="entity-card">'
            f'<div class="entity-title">💰 Facture #{fac.id} — {fac.montant_formate} {badge}</div>'
            f'<div class="entity-field">📝 {fac_desc}</div>'
            f'{client_html}'
            f'{event_html}'
            f'<div class="entity-field">📅 Creee le {fac.date_creation}</div>'
            '</div>'
        )
        st.markdown(fac_card, unsafe_allow_html=True)

        col_pdf, col_m, col_s, _ = st.columns([1, 1, 1, 5])
        with col_pdf:
            pdf_bytes = pdf_service.generer_facture_pdf(fac)
            st.download_button(
                "📄 PDF",
                data=pdf_bytes,
                file_name=f"Facture_FAC-{fac.id:04d}.pdf",
                mime="application/pdf",
                key=f"pdf_f_{fac.id}",
                use_container_width=True,
            )
        with col_m:
            if st.button("✏️ Modifier", key=f"mod_f_{fac.id}", use_container_width=True):
                st.session_state["mode_facture"] = "modification"
                st.session_state["facture_edit_id"] = fac.id
                st.rerun()
        with col_s:
            if st.button("🗑️ Supprimer", key=f"sup_f_{fac.id}", use_container_width=True):
                st.session_state["confirm_sup_facture"] = fac.id
                st.rerun()

        if st.session_state.get("confirm_sup_facture") == fac.id:
            st.warning(f"Confirmer la suppression de la facture #{fac.id} ?")
            col_y, col_n, _ = st.columns([1, 1, 6])
            with col_y:
                if st.button("✅ Confirmer", key=f"oui_f_{fac.id}", type="primary"):
                    invoice_service.supprimer(fac.id)
                    st.session_state.pop("confirm_sup_facture", None)
                    st.success("Facture supprimee.")
                    st.rerun()
            with col_n:
                if st.button("❌ Annuler", key=f"non_f_{fac.id}"):
                    st.session_state.pop("confirm_sup_facture", None)
                    st.rerun()

        st.write("")


def _formulaire_ajout_facture():
    """Formulaire de creation d'une facture independante."""
    st.markdown('<div class="sub-header">➕ Nouvelle facture</div>', unsafe_allow_html=True)

    clients = client_service.lister_pour_selection()

    with st.form("form_ajout_facture"):
        description = st.text_area("Description *", placeholder="Prestation, details...")

        col1, col2 = st.columns(2)
        with col1:
            montant = st.number_input("Montant (EUR) *", min_value=0.0, step=10.0, format="%.2f")
        with col2:
            statut = st.selectbox(
                "Statut",
                list(STATUTS_FACTURE.keys()),
                format_func=lambda x: f"{STATUTS_FACTURE_ICONES.get(x, '')} {STATUTS_FACTURE[x]}",
                key="add_fac_statut",
            )

        options_clients = [{"id": None, "nom": "— Aucun client —"}] + clients
        choix_client = st.selectbox(
            "Client",
            options_clients,
            format_func=lambda x: x["nom"],
            key="add_fac_client",
        )

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        facture = Invoice(
            client_id=choix_client["id"],
            description=description,
            montant=montant,
            statut=statut,
        )
        erreurs = facture.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            invoice_service.creer(facture)
            st.session_state["mode_facture"] = None
            st.success("Facture creee.")
            st.rerun()

    if annuler:
        st.session_state["mode_facture"] = None
        st.rerun()


def _formulaire_modification_facture(facture_id: int):
    """Formulaire de modification d'une facture."""
    fac = invoice_service.obtenir(facture_id)
    if not fac:
        st.error("Facture introuvable.")
        st.session_state["mode_facture"] = None
        return

    st.markdown(f'<div class="sub-header">✏️ Modifier facture #{fac.id}</div>', unsafe_allow_html=True)

    clients = client_service.lister_pour_selection()

    with st.form("form_modif_facture"):
        description = st.text_area("Description *", value=fac.description)

        col1, col2 = st.columns(2)
        with col1:
            montant = st.number_input("Montant (EUR) *", min_value=0.0, step=10.0, value=fac.montant, format="%.2f")
        with col2:
            statuts_keys = list(STATUTS_FACTURE.keys())
            idx = statuts_keys.index(fac.statut) if fac.statut in statuts_keys else 0
            statut = st.selectbox(
                "Statut",
                statuts_keys,
                index=idx,
                format_func=lambda x: f"{STATUTS_FACTURE_ICONES.get(x, '')} {STATUTS_FACTURE[x]}",
                key="mod_fac_statut",
            )

        options_clients = [{"id": None, "nom": "— Aucun client —"}] + clients
        idx_client = 0
        for i, c in enumerate(options_clients):
            if c["id"] == fac.client_id:
                idx_client = i
                break
        choix_client = st.selectbox(
            "Client",
            options_clients,
            index=idx_client,
            format_func=lambda x: x["nom"],
            key="mod_fac_client",
        )

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        modifie = Invoice(
            id=facture_id,
            event_id=fac.event_id,
            client_id=choix_client["id"],
            description=description,
            montant=montant,
            statut=statut,
        )
        erreurs = modifie.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            invoice_service.modifier(modifie)
            st.session_state["mode_facture"] = None
            st.success("Facture modifiee.")
            st.rerun()

    if annuler:
        st.session_state["mode_facture"] = None
        st.rerun()
