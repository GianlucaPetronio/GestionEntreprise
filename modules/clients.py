"""
Module UI Streamlit : Gestion des clients (CRM).
Interface moderne avec cartes et badges.
Logique métier déléguée à client_service.
"""

import streamlit as st
from models.client import Client
from services import client_service, document_service
from utils.helpers import valeur_ou_tiret
from utils.theme import (
    html_section_header,
    html_empty_state,
    html_result_count,
    html_divider,
)


def afficher_page():
    """Point d'entrée : page de gestion des clients."""
    st.markdown(
        html_section_header("👥", "Clients", "Gérez votre base de clients"),
        unsafe_allow_html=True,
    )

    # --- Barre d'actions ---
    col_rech, col_btn = st.columns([3, 1])
    with col_rech:
        recherche = st.text_input(
            "🔍 Rechercher",
            placeholder="Nom, email, téléphone, adresse...",
            key="rech_client",
            label_visibility="collapsed",
        )
    with col_btn:
        if st.button("➕ Nouveau client", use_container_width=True, type="primary"):
            st.session_state["mode_client"] = "ajout"

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Routage ---
    mode = st.session_state.get("mode_client")
    if mode == "ajout":
        _formulaire_ajout()
    elif mode == "modification":
        _formulaire_modification(st.session_state.get("client_edit_id"))
    else:
        _afficher_liste(recherche)


def _afficher_liste(recherche: str):
    """Affiche la liste des clients sous forme de cartes."""
    clients = client_service.lister(recherche)

    if not clients:
        icone = "🔍" if recherche else "👥"
        msg = "Aucun client trouvé pour cette recherche." if recherche else "Aucun client enregistré. Ajoutez votre premier client."
        st.markdown(html_empty_state(icone, msg), unsafe_allow_html=True)
        return

    st.markdown(
        html_result_count(len(clients), "client(s)"),
        unsafe_allow_html=True,
    )

    for c in clients:
        nb_docs = document_service.compter_pour_client(c.id)
        docs_txt = f"📎 {nb_docs} doc(s)" if nb_docs else ""
        notes_html = f'<div class="entity-field">📝 <strong>Notes</strong> {c.notes}</div>' if c.notes else ""

        st.markdown(f"""
        <div class="entity-card">
            <div class="entity-title">👤 {c.nom}</div>
            <div class="entity-field">📞 <strong>Tél.</strong> {valeur_ou_tiret(c.telephone)}</div>
            <div class="entity-field">✉️ <strong>Email</strong> {valeur_ou_tiret(c.email)}</div>
            <div class="entity-field">📍 <strong>Adresse</strong> {valeur_ou_tiret(c.adresse)}</div>
            <div class="entity-field">📅 Créé le {c.date_creation} {docs_txt}</div>
            {notes_html}
        </div>
        """, unsafe_allow_html=True)

        # Boutons sur une seule ligne
        col_v, col_m, col_s, _ = st.columns([1, 1, 1, 5])
        with col_v:
            if st.button("📄 Documents", key=f"docs_c_{c.id}", use_container_width=True):
                pass  # Navigation future possible
        with col_m:
            if st.button("✏️ Modifier", key=f"mod_c_{c.id}", use_container_width=True):
                st.session_state["mode_client"] = "modification"
                st.session_state["client_edit_id"] = c.id
                st.rerun()
        with col_s:
            if st.button("🗑️ Supprimer", key=f"sup_c_{c.id}", use_container_width=True):
                st.session_state["confirm_sup_client"] = c.id
                st.rerun()

        # Confirmation suppression
        if st.session_state.get("confirm_sup_client") == c.id:
            st.warning(f"Confirmer la suppression de **{c.nom}** ? Cette action est irréversible.")
            col_y, col_n, _ = st.columns([1, 1, 6])
            with col_y:
                if st.button("✅ Confirmer", key=f"oui_c_{c.id}", type="primary"):
                    client_service.supprimer(c.id)
                    st.session_state.pop("confirm_sup_client", None)
                    st.success("Client supprimé.")
                    st.rerun()
            with col_n:
                if st.button("❌ Annuler", key=f"non_c_{c.id}"):
                    st.session_state.pop("confirm_sup_client", None)
                    st.rerun()

        st.write("")


def _formulaire_ajout():
    """Formulaire de création d'un client."""
    st.markdown('<div class="sub-header">➕ Nouveau client</div>', unsafe_allow_html=True)

    with st.form("form_ajout_client"):
        nom = st.text_input("Nom *", placeholder="Nom complet du client")

        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("✉️ Email", placeholder="email@exemple.com")
            telephone = st.text_input("📞 Téléphone", placeholder="06 00 00 00 00")
        with col2:
            adresse = st.text_input("📍 Adresse", placeholder="Adresse complète")

        notes = st.text_area("📝 Notes", placeholder="Informations complémentaires...")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        client = Client(nom=nom, email=email, telephone=telephone, adresse=adresse, notes=notes)
        erreurs = client.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            client_service.creer(client)
            st.session_state["mode_client"] = None
            st.success(f"Client « {nom} » ajouté avec succès.")
            st.rerun()

    if annuler:
        st.session_state["mode_client"] = None
        st.rerun()


def _formulaire_modification(client_id: int):
    """Formulaire de modification d'un client."""
    client = client_service.obtenir(client_id)
    if not client:
        st.error("Client introuvable.")
        st.session_state["mode_client"] = None
        return

    st.markdown(f'<div class="sub-header">✏️ Modifier : {client.nom}</div>', unsafe_allow_html=True)

    with st.form("form_modif_client"):
        nom = st.text_input("Nom *", value=client.nom)

        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("✉️ Email", value=client.email)
            telephone = st.text_input("📞 Téléphone", value=client.telephone)
        with col2:
            adresse = st.text_input("📍 Adresse", value=client.adresse)

        notes = st.text_area("📝 Notes", value=client.notes)

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        modifie = Client(id=client_id, nom=nom, email=email, telephone=telephone, adresse=adresse, notes=notes)
        erreurs = modifie.valider()
        if erreurs:
            for e in erreurs:
                st.error(e)
        else:
            client_service.modifier(modifie)
            st.session_state["mode_client"] = None
            st.success(f"Client « {nom} » modifié.")
            st.rerun()

    if annuler:
        st.session_state["mode_client"] = None
        st.rerun()
