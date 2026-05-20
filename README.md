# GP Entretien Exterieurs — Gestion Interne

Application de gestion interne pour **GP Entretien Exterieurs**, entreprise d'entretien d'espaces verts.
Construite avec **Streamlit** (Python) et **SQLite**, cette application locale permet de gerer les clients, documents, outils, planning et la facturation.

---

## Table des matieres

1. [Fonctionnalites](#fonctionnalites)
2. [Architecture du projet](#architecture-du-projet)
3. [Installation](#installation)
4. [Lancement](#lancement)
5. [Modules detailles](#modules-detailles)
   - [Tableau de bord](#tableau-de-bord)
   - [Agenda / Planning](#agenda--planning)
   - [Clients](#clients)
   - [Documents (GED)](#documents-ged)
   - [Outils / Equipements](#outils--equipements)
   - [Factures et generation PDF](#factures-et-generation-pdf)
   - [Configuration Entreprise](#configuration-entreprise)
   - [Integration Notion](#integration-notion)
6. [Base de donnees](#base-de-donnees)
7. [Systeme de theme](#systeme-de-theme)
8. [Structure des fichiers](#structure-des-fichiers)
9. [Stack technique](#stack-technique)

---

## Fonctionnalites

### Gestion des clients (CRM)
- Creer, modifier, supprimer des clients
- Recherche par nom, email, telephone, adresse
- Notes libres par client

### Gestion des documents (GED)
- Upload de fichiers (PDF, images, Office, CSV, ZIP, TXT)
- Association a un client
- Suivi de statut : recu, en cours, envoye, archive
- Previsualisation PDF et images dans le navigateur
- Telechargement et remplacement de fichiers

### Gestion des outils / equipements
- Inventaire du materiel avec description
- Suivi d'etat : disponible, en utilisation, en maintenance
- Assignation a un chantier ou vehicule
- Filtrage et recherche

### Agenda / Planning avance
- Creation d'evenements avec titre, dates, client, type de travail
- Vues : **liste**, **semaine** (7 jours avec navigation), **jour**
- Assignation de plusieurs outils par evenement
- Suivi de statut : planifie, en cours, termine, annule
- Notes d'intervention
- Filtrage par client et par statut
- Generation de facture directement depuis un evenement

### Facturation
- Creation de factures liees ou independantes
- Statuts : brouillon, en attente, paye
- Totaux par statut sur le tableau de bord
- **Generation de factures PDF** avec template professionnel pre-defini
- Telechargement PDF en un clic

### Integration Notion (optionnelle)
- Synchronisation des evenements vers une base de donnees Notion
- Configuration de la cle API et de l'ID de base
- Test de connexion integre
- Synchronisation individuelle ou en masse

### Tableau de bord
- 5 cartes de statistiques (evenements, factures, clients, documents, outils)
- Prochains evenements a venir
- Repartition par statut (evenements, documents, outils)
- Suivi financier des factures
- Derniers clients ajoutes

### Recherche globale
- Recherche dans la sidebar a travers tous les modules
- Resultats groupes par type (evenements, clients, documents, outils, factures)

### Theme clair / sombre
- Bascule via toggle dans la sidebar
- CSS complet genere dynamiquement
- Palette de couleurs coherente (vert accent)

---

## Architecture du projet

L'application suit une **architecture en 3 couches** avec separation claire des responsabilites :

```
Streamlit UI (modules/)          <-- Interface utilisateur
       |
Services (services/)             <-- Logique metier et acces BD
       |
Modeles (models/)                <-- Structures de donnees et validation
       |
Base de donnees (database/)      <-- SQLite, schema, connexion
```

**Principes :**
- Les **modules UI** n'accedent jamais directement a la base de donnees
- Les **services** sont independants de Streamlit (testables, reutilisables)
- Les **modeles** sont des `dataclass` Python avec validation et serialisation
- Le **theme** est centralise dans un seul fichier

---

## Installation

### Pre-requis
- Python 3.12 ou superieur
- pip (gestionnaire de paquets Python)

### Etapes

```bash
# 1. Cloner ou copier le projet
cd GestionEntreprise

# 2. Installer les dependances
pip install -r requirements.txt
```

### Dependances
| Paquet     | Usage                          |
|------------|--------------------------------|
| `streamlit`| Framework web (interface)      |
| `fpdf2`    | Generation de factures PDF     |

---

## Lancement

```bash
python -m streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur a l'adresse :
- **Local** : http://localhost:8501
- **Reseau** : http://<votre-ip>:8501

La base de donnees SQLite et les dossiers necessaires (`data/`, `data/uploads/`) sont crees automatiquement au premier lancement.

---

## Modules detailles

### Tableau de bord

Page d'accueil avec vue d'ensemble :
- **5 cartes statistiques** : nombre d'evenements, factures, clients, documents, outils
- **Prochains evenements** : les 5 prochains evenements planifies ou en cours (a partir d'aujourd'hui)
- **Repartitions** : evenements par statut, documents par statut, outils par etat
- **Factures** : montants totaux par statut (brouillon, en attente, paye)
- **Derniers clients** : les 5 clients les plus recemment ajoutes

### Agenda / Planning

Accessible via l'onglet **"Agenda"** dans la sidebar. Organise en deux sous-onglets :

#### Onglet Agenda
- **Barre d'actions** : choix de vue (Liste/Semaine/Jour), filtre par client, bouton creation
- **Vue Liste** : tous les evenements avec recherche et filtre par statut
- **Vue Semaine** : navigation semaine par semaine, groupement par jour avec expanders
- **Vue Jour** : navigation jour par jour
- **Carte evenement** : titre, horaire, type, client, badge de statut, boutons (Detail, Modifier, Facturer, Supprimer)
- **Detail evenement** : informations completes, outils associes, factures liees, bouton sync Notion

#### Onglet Factures
- Totaux par statut en haut de page
- Liste des factures avec recherche et filtre
- Boutons : telecharger PDF, modifier, supprimer
- Creation de facture independante

#### Champs d'un evenement
| Champ          | Type       | Obligatoire | Description                              |
|----------------|------------|-------------|------------------------------------------|
| Titre          | Texte      | Oui         | Nom de l'intervention                    |
| Date debut     | Date+Heure | Oui         | Debut de l'intervention                  |
| Date fin       | Date+Heure | Oui         | Fin de l'intervention                    |
| Client         | Selection  | Non         | Client associe (depuis la liste clients) |
| Type de travail| Selection  | Non         | Entretien, Tonte, Taille, Debroussaillage, Nettoyage, Plantation, Amenagement, Autre |
| Outils         | Multi-sel. | Non         | Outils utilises (depuis l'inventaire)    |
| Statut         | Selection  | Oui         | Planifie, En cours, Termine, Annule      |
| Description    | Texte long | Non         | Details de l'intervention                |
| Notes          | Texte long | Non         | Notes d'intervention / observations      |

### Clients

- **Liste** avec recherche textuelle
- **Creation** : nom (obligatoire), email, telephone, adresse, notes
- **Modification** : formulaire pre-rempli
- **Suppression** : avec confirmation

### Documents (GED)

- **Upload** : 13 types de documents (Devis, Facture client, Photo chantier, Contrat, etc.)
- **Formats** : PDF, JPG, PNG, DOCX, XLSX, CSV, ZIP, TXT...
- **Statuts** : recu, en cours, envoye, archive
- **Previsualisation** : PDF (iframe), images (direct), autres (message)
- **Association** a un client
- **Remplacement** de fichier sans perdre les metadonnees

### Outils / Equipements

- **Liste** avec recherche et filtre par etat
- **Etats** : Disponible (vert), En utilisation (bleu), En maintenance (orange)
- **Assignation** : chantier, vehicule, lieu de stockage
- **Badges visuels** colores selon l'etat

### Factures et generation PDF

Chaque facture peut etre telechargee en **PDF professionnel** contenant :
- **En-tete** : bandeau vert, nom de l'entreprise, coordonnees completes
- **Numero de facture** automatique (FAC-0001, FAC-0002...)
- **Bloc client** : nom du client facture
- **Tableau des prestations** : description, quantite, prix unitaire, total
- **Total general**
- **Conditions de paiement**
- **Pied de page** : mention legale, date de generation

Les informations de l'entreprise sont configurables dans la page **"Entreprise"**.

#### Champs d'une facture
| Champ       | Type       | Description                          |
|-------------|------------|--------------------------------------|
| Description | Texte      | Description de la prestation         |
| Montant     | Decimal    | Montant en EUR                       |
| Statut      | Selection  | Brouillon, En attente, Paye         |
| Client      | Selection  | Client facture                       |
| Evenement   | Automatique| Lie si cree depuis un evenement      |

### Configuration Entreprise

Page **"Entreprise"** dans la sidebar. Les informations configurees ici apparaissent sur les factures PDF :

| Champ           | Description                                    |
|-----------------|------------------------------------------------|
| Nom             | Nom de l'entreprise                            |
| Adresse         | Adresse postale                                |
| Code postal     | Code postal                                    |
| Ville           | Ville                                          |
| Telephone       | Numero de telephone                            |
| Email           | Adresse email                                  |
| SIRET           | Numero d'identification (SIRET, TVA, BCE...)   |
| Mention legale  | Texte en pied de facture                       |

Un bouton **"Telecharger l'apercu PDF"** permet de verifier le rendu avant d'envoyer une facture reelle.

La configuration est stockee dans `data/entreprise_config.json`.

### Integration Notion

Page **"Notion"** dans la sidebar. Permet de synchroniser les evenements avec une base Notion.

#### Configuration requise
1. Creer une integration sur [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Creer une base de donnees Notion avec les proprietes :
   - **Titre** (type: title)
   - **Date** (type: date)
   - **Client** (type: rich_text)
   - **Statut** (type: select)
   - **Type** (type: select)
3. Partager la base avec l'integration
4. Renseigner la cle API et l'ID de base dans l'application

#### Fonctionnalites
- Test de connexion
- Synchronisation individuelle (depuis le detail d'un evenement)
- Synchronisation en masse (tous les evenements)
- Activation/desactivation

La configuration est stockee dans `data/notion_config.json`.

---

## Base de donnees

**Moteur** : SQLite 3 (fichier local `data/gestion.db`)

### Schema

#### Table `clients`
| Colonne       | Type    | Contrainte                    |
|---------------|---------|-------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT     |
| nom           | TEXT    | NOT NULL                      |
| email         | TEXT    | DEFAULT ''                    |
| telephone     | TEXT    | DEFAULT ''                    |
| adresse       | TEXT    | DEFAULT ''                    |
| notes         | TEXT    | DEFAULT ''                    |
| date_creation | TEXT    | NOT NULL                      |

#### Table `documents`
| Colonne       | Type    | Contrainte                              |
|---------------|---------|-----------------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT               |
| nom_fichier   | TEXT    | NOT NULL (nom UUID sur disque)          |
| nom_original  | TEXT    | NOT NULL (nom d'origine)                |
| type_document | TEXT    | DEFAULT ''                              |
| client_id     | INTEGER | FK -> clients(id) ON DELETE SET NULL    |
| statut        | TEXT    | DEFAULT 'recu'                          |
| notes         | TEXT    | DEFAULT ''                              |
| date_ajout    | TEXT    | NOT NULL                                |

#### Table `outils`
| Colonne     | Type    | Contrainte                |
|-------------|---------|---------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT |
| nom         | TEXT    | NOT NULL                  |
| description | TEXT    | DEFAULT ''                |
| etat        | TEXT    | DEFAULT 'disponible'      |
| assignation | TEXT    | DEFAULT ''                |
| date_ajout  | TEXT    | NOT NULL                  |

#### Table `events`
| Colonne       | Type    | Contrainte                              |
|---------------|---------|-----------------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT               |
| titre         | TEXT    | NOT NULL                                |
| description   | TEXT    | DEFAULT ''                              |
| date_debut    | TEXT    | NOT NULL (format YYYY-MM-DD HH:MM)     |
| date_fin      | TEXT    | NOT NULL (format YYYY-MM-DD HH:MM)     |
| client_id     | INTEGER | FK -> clients(id) ON DELETE SET NULL    |
| type_travail  | TEXT    | DEFAULT ''                              |
| statut        | TEXT    | DEFAULT 'planifie'                      |
| notes         | TEXT    | DEFAULT ''                              |
| date_creation | TEXT    | NOT NULL                                |

#### Table `event_tools` (relation N:N)
| Colonne  | Type    | Contrainte                              |
|----------|---------|-----------------------------------------|
| id       | INTEGER | PRIMARY KEY AUTOINCREMENT               |
| event_id | INTEGER | FK -> events(id) ON DELETE CASCADE      |
| outil_id | INTEGER | FK -> outils(id) ON DELETE CASCADE      |
|          |         | UNIQUE(event_id, outil_id)              |

#### Table `invoices`
| Colonne       | Type    | Contrainte                              |
|---------------|---------|-----------------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT               |
| event_id      | INTEGER | FK -> events(id) ON DELETE SET NULL     |
| client_id     | INTEGER | FK -> clients(id) ON DELETE SET NULL    |
| description   | TEXT    | DEFAULT ''                              |
| montant       | REAL    | DEFAULT 0.0                             |
| statut        | TEXT    | DEFAULT 'brouillon'                     |
| date_creation | TEXT    | NOT NULL                                |

### Relations

```
clients  1---N  documents     (client_id)
clients  1---N  events        (client_id)
clients  1---N  invoices      (client_id)
events   1---N  invoices      (event_id)
events   N---N  outils        (via event_tools)
```

---

## Systeme de theme

L'application supporte deux themes : **clair** et **sombre**.

Le toggle se trouve dans la sidebar. Le CSS complet est genere dynamiquement par `utils/theme.py` a partir d'une palette centralisee.

### Palette (extrait)
| Variable       | Clair      | Sombre     |
|----------------|------------|------------|
| Fond principal | `#F4F6F8`  | `#0E1117`  |
| Fond carte     | `#FFFFFF`  | `#1A1F2B`  |
| Accent (vert)  | `#1B6B20`  | `#4CAF50`  |
| Texte primaire | `#111827`  | `#E6EDF3`  |
| Bordure        | `#D0D5DD`  | `#2D333B`  |

### Composants CSS
- `.stat-card` : cartes de statistiques du dashboard
- `.entity-card` : cartes d'entites (bordure verte a gauche)
- `.badge` : indicateurs de statut colores
- `.section-header` : titres de pages
- `.mini-metric` : metriques compactes
- `.empty-state` : etat vide centre

---

## Structure des fichiers

```
GestionEntreprise/
|
|-- app.py                          # Point d'entree Streamlit (routage, dashboard, config)
|-- requirements.txt                # Dependances Python
|-- README.md                       # Ce fichier
|
|-- database/
|   |-- __init__.py
|   |-- db.py                       # Connexion SQLite, initialisation du schema
|
|-- models/                         # Modeles de donnees (dataclass Python)
|   |-- __init__.py
|   |-- client.py                   # Modele Client
|   |-- document.py                 # Modele Document
|   |-- outil.py                    # Modele Outil
|   |-- event.py                    # Modele Event (evenement agenda)
|   |-- invoice.py                  # Modele Invoice (facture)
|
|-- services/                       # Logique metier (CRUD, requetes)
|   |-- __init__.py
|   |-- client_service.py           # Operations clients
|   |-- document_service.py         # Operations documents + fichiers
|   |-- outil_service.py            # Operations outils
|   |-- event_service.py            # Operations evenements + outils associes
|   |-- invoice_service.py          # Operations factures
|   |-- pdf_service.py              # Generation de factures PDF
|   |-- notion_service.py           # Integration API Notion
|
|-- modules/                        # Pages UI Streamlit
|   |-- __init__.py
|   |-- clients.py                  # Page gestion des clients
|   |-- documents.py                # Page gestion des documents
|   |-- outils.py                   # Page gestion des outils
|   |-- agenda.py                   # Page agenda + factures
|
|-- utils/                          # Utilitaires partages
|   |-- __init__.py
|   |-- helpers.py                  # Chemins, gestion fichiers, constantes
|   |-- theme.py                    # Palette de couleurs, CSS, composants HTML
|
|-- data/                           # Donnees (cree automatiquement)
    |-- gestion.db                  # Base de donnees SQLite
    |-- uploads/                    # Fichiers uploades (noms UUID)
    |-- entreprise_config.json      # Configuration entreprise (factures)
    |-- notion_config.json          # Configuration API Notion
```

---

## Stack technique

| Composant       | Technologie           | Version    |
|-----------------|-----------------------|------------|
| Langage         | Python                | 3.12+      |
| Interface web   | Streamlit             | latest     |
| Base de donnees | SQLite 3              | integre    |
| Generation PDF  | fpdf2                 | latest     |
| API externe     | Notion API            | 2022-06-28 |
| Hebergement     | Local (aucun serveur) | -          |

---

## Donnees et sauvegarde

Toutes les donnees sont stockees localement dans le dossier `data/` :
- `gestion.db` : base de donnees SQLite (clients, documents, outils, evenements, factures)
- `uploads/` : fichiers physiques uploades (nommes par UUID)
- `entreprise_config.json` : parametres de l'entreprise
- `notion_config.json` : parametres de connexion Notion

Pour sauvegarder l'application, il suffit de copier l'integralite du dossier `GestionEntreprise/`.

---

*v2.0 — Application locale de gestion pour GP Entretien Exterieurs*
"# GestionEntreprise" 
