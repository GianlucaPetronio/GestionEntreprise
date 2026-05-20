"""
Module UI Streamlit : Gestion des documents (GED).
Interface moderne avec cartes, badges de statut et prévisualisation.
Logique métier déléguée à document_service.
"""

import base64
import streamlit as st
from models.document import Document, STATUTS, TYPES, EXTENSIONS_AUTORISEES
from services import client_service, document_service
from utils.helpers import chemin_fichier_upload, fichier_existe
from utils.theme import (
    html_section_header,
    html_empty_state,
    html_result_count,
    html_badge,
    html_divider,
)


def afficher_page():
    """Point d'entrée : page de gestion des documents."""
    st.markdown(
        html_section_header("📄", "Documents", "Gestion électronique de vos documents"),
        unsafe_allow_html=True,
    )

    # --- Filtres (tous avec label visible pour alignement) ---
    col_rech, col_stat, col_cli, col_btn = st.columns([2, 1, 1, 1])
    with col_rech:
        recherche = st.text_input(
            "Recherche",
            placeholder="Nom de fichier, type...",
            key="rech_doc",
        )
    with col_stat:
        opts_statut = ["Tous les statuts"] + list(STATUTS.values())
        choix_statut = st.selectbox("Statut", opts_statut, key="filtre_statut_doc")
        filtre_statut = _label_vers_cle(choix_statut, STATUTS)
    with col_cli:
        clients = client_service.lister_pour_selection()
        noms = {"Tous les clients": None}
        for c in clients:
            noms[c["nom"]] = c["id"]
        choix_cli = st.selectbox("Client", list(noms.keys()), key="filtre_cli_doc")
        filtre_client_id = noms[choix_cli]
    with col_btn:
        st.write("")  # Aligner avec les labels
        st.write("")
        if st.button("➕ Nouveau document", type="primary", use_container_width=True):
            st.session_state["mode_doc"] = "ajout"

    st.markdown(html_divider(), unsafe_allow_html=True)

    # --- Routage ---
    mode = st.session_state.get("mode_doc")
    if mode == "ajout":
        _formulaire_upload()
    elif mode == "modification":
        _formulaire_modification(st.session_state.get("doc_edit_id"))
    else:
        _afficher_liste(recherche, filtre_statut, filtre_client_id)


def _label_vers_cle(label: str, mapping: dict) -> str:
    for cle, val in mapping.items():
        if val == label:
            return cle
    return ""


def _afficher_visualisation(doc):
    """
    Affiche le document directement dans la page, sans téléchargement.
    PDF : intégré dans un iframe. Images : affichées. Autres : message.
    """
    chemin = chemin_fichier_upload(doc.nom_fichier)
    ext = doc.nom_original.rsplit(".", 1)[-1].lower() if "." in doc.nom_original else ""

    # Bouton pour fermer la visualisation
    if st.button("❌ Fermer l'aperçu", key=f"fermer_voir_{doc.id}"):
        st.session_state.pop("voir_doc_id", None)
        st.rerun()

    with open(chemin, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    if ext == "pdf":
        pdf_html = f'<iframe src="data:application/pdf;base64,{data}" width="100%" height="700" style="border:1px solid #555; border-radius:8px;"></iframe>'
        st.markdown(pdf_html, unsafe_allow_html=True)

    elif ext in ("png", "jpg", "jpeg", "gif", "bmp", "webp"):
        st.image(chemin, caption=doc.nom_original, use_container_width=True)

    elif ext == "txt":
        with open(chemin, "r", encoding="utf-8", errors="replace") as tf:
            st.code(tf.read(), language=None)

    else:
        st.info(f"L'aperçu n'est pas disponible pour les fichiers .{ext}. Utilisez le bouton Télécharger.")



def _afficher_liste(recherche: str, filtre_statut: str, filtre_client_id):
    """Affiche la liste des documents sous forme de cartes."""
    docs = document_service.lister(recherche, filtre_statut, filtre_client_id)

    if not docs:
        icone = "🔍" if (recherche or filtre_statut or filtre_client_id) else "📄"
        msg = "Aucun document trouvé." if (recherche or filtre_statut or filtre_client_id) else "Aucun document. Ajoutez votre premier document."
        st.markdown(html_empty_state(icone, msg), unsafe_allow_html=True)
        return

    st.markdown(html_result_count(len(docs), "document(s)"), unsafe_allow_html=True)

    for doc in docs:
        client_txt = doc.nom_client or "Aucun client"
        badge = html_badge(doc.statut, doc.statut_label)
        notes_html = f'<div class="entity-field">📝 <strong>Notes</strong> {doc.notes}</div>' if doc.notes else ""

        st.markdown(f"""
        <div class="entity-card">
            <div class="entity-title">📄 {doc.nom_original} {badge}</div>
            <div class="entity-field">📂 <strong>Type</strong> {doc.type_document or '—'}</div>
            <div class="entity-field">👤 <strong>Client</strong> {client_txt}</div>
            <div class="entity-field">📅 Ajouté le {doc.date_ajout}</div>
            {notes_html}
        </div>
        """, unsafe_allow_html=True)

        # 4 boutons sur une seule ligne
        col_voir, col_dl, col_m, col_s, _ = st.columns([1, 1, 1, 1, 4])
        fichier_present = fichier_existe(doc.nom_fichier)
        with col_voir:
            if fichier_present:
                if st.button("👁️ Voir", key=f"voir_{doc.id}", use_container_width=True):
                    st.session_state["voir_doc_id"] = doc.id
            else:
                st.button("👁️ Voir", key=f"voir_{doc.id}", disabled=True, use_container_width=True)
        with col_dl:
            if fichier_present:
                with open(chemin_fichier_upload(doc.nom_fichier), "rb") as f:
                    st.download_button(
                        "⬇️ Télécharger", f.read(),
                        file_name=doc.nom_original,
                        key=f"dl_{doc.id}",
                        use_container_width=True,
                    )
            else:
                st.button("⬇️ Télécharger", key=f"miss_{doc.id}", disabled=True, use_container_width=True)
        with col_m:
            if st.button("✏️ Modifier", key=f"mod_d_{doc.id}", use_container_width=True):
                st.session_state["mode_doc"] = "modification"
                st.session_state["doc_edit_id"] = doc.id
                st.rerun()
        with col_s:
            if st.button("🗑️ Supprimer", key=f"sup_d_{doc.id}", use_container_width=True):
                st.session_state["confirm_sup_doc"] = doc.id
                st.rerun()

        # Zone de visualisation (s'affiche quand on clique sur Voir)
        if st.session_state.get("voir_doc_id") == doc.id and fichier_present:
            _afficher_visualisation(doc)

        # Confirmation suppression
        if st.session_state.get("confirm_sup_doc") == doc.id:
            st.warning(f"Supprimer **{doc.nom_original}** ? Le fichier sera effacé du disque.")
            col_y, col_n, _ = st.columns([1, 1, 6])
            with col_y:
                if st.button("✅ Confirmer", key=f"oui_d_{doc.id}", type="primary"):
                    document_service.supprimer(doc.id)
                    st.session_state.pop("confirm_sup_doc", None)
                    st.success("Document supprimé.")
                    st.rerun()
            with col_n:
                if st.button("❌ Annuler", key=f"non_d_{doc.id}"):
                    st.session_state.pop("confirm_sup_doc", None)
                    st.rerun()

        st.write("")


def _formulaire_upload():
    """Formulaire d'upload d'un nouveau document."""
    st.markdown('<div class="sub-header">➕ Nouveau document</div>', unsafe_allow_html=True)

    fichier = st.file_uploader(
        "Choisir un fichier",
        type=EXTENSIONS_AUTORISEES,
        key="upload_fichier",
    )

    with st.form("form_upload_doc"):
        col1, col2 = st.columns(2)
        with col1:
            type_doc = st.selectbox("📂 Type de document", TYPES)
            statut = st.selectbox(
                "📌 Statut", list(STATUTS.keys()),
                format_func=lambda x: STATUTS[x],
            )
        with col2:
            clients = client_service.lister_pour_selection()
            options = {"— Aucun client —": None}
            for c in clients:
                options[c["nom"]] = c["id"]
            choix = st.selectbox("👤 Associer à un client", list(options.keys()))
            client_id = options[choix]

        notes = st.text_area("📝 Notes", placeholder="Informations complémentaires...")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        if not fichier:
            st.error("Veuillez sélectionner un fichier.")
        else:
            doc = Document(
                nom_original=fichier.name,
                type_document=type_doc,
                client_id=client_id,
                statut=statut,
                notes=notes,
            )
            document_service.creer(doc, fichier.getbuffer())
            st.session_state["mode_doc"] = None
            st.success(f"Document « {fichier.name} » ajouté.")
            st.rerun()

    if annuler:
        st.session_state["mode_doc"] = None
        st.rerun()


def _formulaire_modification(doc_id: int):
    """Formulaire de modification d'un document (métadonnées + remplacement fichier)."""
    doc = document_service.obtenir(doc_id)
    if not doc:
        st.error("Document introuvable.")
        st.session_state["mode_doc"] = None
        return

    st.markdown(f'<div class="sub-header">✏️ Modifier : {doc.nom_original}</div>', unsafe_allow_html=True)

    # Fichier actuel + option de remplacement (hors du form, contrainte Streamlit)
    st.info(f"📎 Fichier actuel : **{doc.nom_original}**")
    nouveau_fichier = st.file_uploader(
        "Remplacer le fichier (optionnel)",
        type=EXTENSIONS_AUTORISEES,
        key="remplacement_fichier",
        help="Laissez vide pour conserver le fichier actuel.",
    )

    with st.form("form_modif_doc"):
        col1, col2 = st.columns(2)
        with col1:
            idx_type = TYPES.index(doc.type_document) if doc.type_document in TYPES else 0
            type_doc = st.selectbox("📂 Type", TYPES, index=idx_type)

            statuts_keys = list(STATUTS.keys())
            idx_statut = statuts_keys.index(doc.statut) if doc.statut in statuts_keys else 0
            statut = st.selectbox(
                "📌 Statut", statuts_keys, index=idx_statut,
                format_func=lambda x: STATUTS[x],
            )
        with col2:
            clients = client_service.lister_pour_selection()
            options = {"— Aucun client —": None}
            for c in clients:
                options[c["nom"]] = c["id"]
            idx_client = 0
            for i, (_, cid) in enumerate(options.items()):
                if cid == doc.client_id:
                    idx_client = i
                    break
            choix = st.selectbox("👤 Client", list(options.keys()), index=idx_client)
            client_id = options[choix]

        notes = st.text_area("📝 Notes", value=doc.notes or "")

        st.markdown("")
        col_s, col_a, _ = st.columns([1, 1, 4])
        with col_s:
            soumettre = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        with col_a:
            annuler = st.form_submit_button("Annuler", use_container_width=True)

    if soumettre:
        # Mettre à jour les métadonnées
        modifie = Document(id=doc_id, type_document=type_doc, client_id=client_id, statut=statut, notes=notes)
        document_service.modifier(modifie)

        # Remplacer le fichier si un nouveau a été fourni
        if nouveau_fichier:
            document_service.remplacer_fichier(doc_id, nouveau_fichier.getbuffer(), nouveau_fichier.name)
            st.session_state["mode_doc"] = None
            st.success(f"Document modifié et fichier remplacé par « {nouveau_fichier.name} ».")
        else:
            st.session_state["mode_doc"] = None
            st.success("Document modifié.")
        st.rerun()

    if annuler:
        st.session_state["mode_doc"] = None
        st.rerun()
