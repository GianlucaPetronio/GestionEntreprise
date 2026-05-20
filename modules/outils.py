"""
Module UI Streamlit : Gestion des outils / équipements.
Interface moderne avec cartes et badges d'état.
Logique métier déléguée à outil_service.
"""

import streamlit as st
from models.outil import Outil, ETATS, ETATS_ICONES
from services import outil_service
from utils.helpers import valeur_ou_tiret
from utils.theme import (
    html_section_header,
    html_empty_state,
    html_result_count,
    html_badge,
    html_divider,
)


def afficher_page():
    """Point d'entrée : page de gestion des outils."""
    st.markdown(
        html_section_header("🔧", "Outils / Équipements", "Suivi de votre matériel"),
        unsafe_allow_html=True,
    )

    # --- Filtres ---
    col_rech, col_etat, col_btn = st.columns([2, 1, 1])
    with col_rech:
        recherche = st.text_input(
            "🔍 Rechercher",
            placeholder="Nom, description...",
            key="rech_outil",
            label_visibility="collapsed",
        )
    with col_etat:
        opts_etat = ["Tous les états"] + list(ETATS.values())
        choix_etat = st.selectbox("État", opts_etat, key="filtre_etat_outil")
        filtre_etat = _label_vers_cle(choix_etat, ETATS)
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Nouvel outil", use_container_width=True, type="primary"):
            st.session_state["mode_outil"] = "ajout"

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Routage ---
    mode = st.session_state.get("mode_outil")
    if mode == "ajout":
        _formulaire_ajout()
    elif mode == "modification":
        _formulaire_modification(st.session_state.get("outil_edit_id"))
    else:
        _afficher_liste(recherche, filtre_etat)


def _label_vers_cle(label: str, mapping: dict) -> str:
    for cle, val in mapping.items():
        if val == label:
            return cle
    return ""


def _afficher_liste(recherche: str, filtre_etat: str):
    """Affiche la liste des outils sous forme de cartes."""
    outils = outil_service.lister(recherche, filtre_etat)

    if not outils:
        icone = "🔍" if (recherche or filtre_etat) else "🔧"
        msg = "Aucun outil trouvé." if (recherche or filtre_etat) else "Aucun outil enregistré. Ajoutez votre premier outil."
        st.markdown(html_empty_state(icone, msg), unsafe_allow_html=True)
        return

    st.markdown(html_result_count(len(outils), "outil(s)"), unsafe_allow_html=True)

    for o in outils:
        badge = html_badge(o.etat, f"{o.etat_icone} {o.etat_label}")
        assign_html = f'<div class="entity-field">📍 <strong>Assigné</strong> {o.assignation}</div>' if o.assignation else ""
        desc_text = o.description.replace("\n", "<br>") if o.description else ""
        desc_html = f'<div class="entity-field">📝 <strong>Description</strong><br>{desc_text}</div>' if desc_text else ""

        card_html = (
            '<div class="entity-card">'
            f'<div class="entity-title">🔧 {o.nom} {badge}</div>'
            f'<div class="entity-field">📅 Ajouté le {o.date_ajout}</div>'
            f'{assign_html}'
            f'{desc_html}'
            '</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        # 2 boutons sur une seule ligne
        col_m, col_s, _ = st.columns([1, 1, 6])
        with col_m:
            if st.button("✏️ Modifier", key=f"mod_o_{o.id}", use_container_width=True):
                st.session_state["mode_outil"] = "modification"
                st.session_state["outil_edit_id"] = o.id
                st.rerun()
        with col_s:
            if st.button("🗑️ Supprimer", key=f"sup_o_{o.id}", use_container_width=True):
                st.session_state["confirm_sup_outil"] = o.id
                st.rerun()

        # Confirmation suppression
        if st.session_state.get("confirm_sup_outil") == o.id:
            st.warning(f"Confirmer la suppression de **{o.nom}** ?")
            col_y, col_n, _ = st.columns([1, 1, 6])
            with col_y:
                if st.button("✅ Confirmer", key=f"oui_o_{o.id}", type="primary"):
                    outil_service.supprimer(o.id)
                    st.session_state.pop("confirm_sup_outil", None)
                    st.success("Outil supprimé.")
                    st.rerun()
            with col_n:
                if st.button("❌ Annuler", key=f"non_o_{o.id}"):
                    st.session_state.pop("confirm_sup_outil", None)
                    st.rerun()

        st.write("")


def _formulaire_ajout():
    """Formulaire de création d'un outil."""
    st.markdown('<div class="sub-header">➕ Nouvel outil</div>', unsafe_allow_html=True)

    with st.form("form_ajout_outil"):
        nom = st.text_input("Nom de l'outil *", placeholder="Ex : Tondeuse Husqvarna LC353V")
        description = st.text_area("📝 Description", placeholder="Modèle, caractéristiques...")

        col1, col2 = st.columns(2)
        with col1:
            etat = st.selectbox(
                "📌 État", list(ETATS.keys()),
                format_func=lambda x: f"{ETATS_ICONES.get(x, '')} {ETATS[x]}",
            )
        with col2:
            assignation = st.text_input("📍 Assignation", placeholder="Chantier, véhicule, lieu...")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        outil = Outil(nom=nom, description=description, etat=etat, assignation=assignation)
        erreurs = outil.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            outil_service.creer(outil)
            st.session_state["mode_outil"] = None
            st.success(f"Outil « {nom} » ajouté.")
            st.rerun()

    if annuler:
        st.session_state["mode_outil"] = None
        st.rerun()


def _formulaire_modification(outil_id: int):
    """Formulaire de modification d'un outil."""
    outil = outil_service.obtenir(outil_id)
    if not outil:
        st.error("Outil introuvable.")
        st.session_state["mode_outil"] = None
        return

    st.markdown(f'<div class="sub-header">✏️ Modifier : {outil.nom}</div>', unsafe_allow_html=True)

    with st.form("form_modif_outil"):
        nom = st.text_input("Nom *", value=outil.nom)
        description = st.text_area("📝 Description", value=outil.description or "")

        col1, col2 = st.columns(2)
        with col1:
            etats_keys = list(ETATS.keys())
            idx = etats_keys.index(outil.etat) if outil.etat in etats_keys else 0
            etat = st.selectbox(
                "📌 État", etats_keys, index=idx,
                format_func=lambda x: f"{ETATS_ICONES.get(x, '')} {ETATS[x]}",
            )
        with col2:
            assignation = st.text_input("📍 Assignation", value=outil.assignation or "")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        modifie = Outil(id=outil_id, nom=nom, description=description, etat=etat, assignation=assignation)
        erreurs = modifie.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            outil_service.modifier(modifie)
            st.session_state["mode_outil"] = None
            st.success(f"Outil « {nom} » modifié.")
            st.rerun()

    if annuler:
        st.session_state["mode_outil"] = None
        st.rerun()
