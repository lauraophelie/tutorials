Voici un exemple **complet et concret** de ta spec technique finale, adapté à ton contexte réel (Odoo → Spark/Airflow → DWH PostgreSQL → Power BI, avec SSO et Docker). Tu peux t'en servir comme modèle direct.

---

# Spécification Technique — Plateforme Odoo : Module Reporting & Dashboard

## 0. Vision et périmètre

Cette spécification couvre la chaîne data de bout en bout de la plateforme Odoo : de l'ingestion des données sources (Odoo et legacy) jusqu'à la restitution via Power BI, en incluant les aspects de sécurité (SSO, RLS) et d'exploitation (Docker, monitoring). Elle s'inscrit dans le cadre du remplacement de l'ancien logiciel métier par une plateforme personnalisée.

**Périmètre inclus :** ETL (Spark + Airflow), Data Warehouse (PostgreSQL), Data Marts, Reporting Power BI, authentification SSO, contrôle d'accès, environnements, monitoring.
**Périmètre exclu :** développement fonctionnel Odoo, infrastructure réseau, support utilisateur.

---

## 1. Historique du document

| Version | Date       | Rédacteur | Commentaire            |
| ------- | ---------- | --------- | ---------------------- |
| 0.1     | 12/05/2025 | [Toi]     | Création initiale      |
| 0.2     | 19/05/2025 | [Toi]     | Ajustements techniques |
| 1.0     | 26/05/2025 | [Toi]     | Version validée        |

## 2. Validation du document

|                | Nom | Fonction | Signature | Date |
| -------------- | --- | -------- | --------- | ---- |
| Référent IT    |     |          |           |      |
| Responsable IT |     |          |           |      |

---

## 3. Architecture globale

### 3.1 Diagramme d'architecture

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Sources          │   │ ETL              │   │ Data Warehouse   │   │ Restitution      │
│                  │──▶│                  │──▶│                  │──▶│                  │
│ • Odoo (réplica) │   │ • Apache Spark   │   │ • PostgreSQL     │   │ • Power BI       │
│ • Legacy         │   │ • Apache Airflow │   │   - staging      │   │ • SSO Entra ID   │
│ • Fichiers/API   │   │ • Docker         │   │   - dwh          │   │ • RLS            │
└──────────────────┘   └──────────────────┘   │   - dm           │   └──────────────────┘
                                              └──────────────────┘
                    ┌─────────────────────────────────────────────┐
                    │ Transverse : Monitoring, Sécurité, Alerting │
                    └─────────────────────────────────────────────┘
```

### 3.2 Description des composants

| Composant | Type | Description / Rôle | Interfaces / Liaisons |
|-----------|------|--------------------|-----------------------|
| Odoo (réplica PostgreSQL) | Source | Base transactionnelle en lecture seule | Spark (JDBC) |
| Legacy (ancien logiciel) | Source | Données historiques à migrer | Export CSV / dump SQL |
| Apache Spark | Service ETL | Extraction, transformation, chargement distribué | Sources, DWH |
| Apache Airflow | Orchestrateur | Planification et supervision des jobs ETL | Spark, monitoring |
| Docker | Middleware | Conteneurisation Airflow + Spark (DEV/PROD) | Tous composants |
| PostgreSQL (DWH) | SGBD | Stockage modélisé (staging, dwh, dm) | Spark, Power BI |
| Power BI Service | Reporting | Dashboards, datasets partagés, RLS | DWH (gateway), Entra ID |
| Microsoft Entra ID | Sécurité | SSO, authentification, groupes | Power BI, utilisateurs |
| Power BI Gateway | Middleware | Passerelle sécurisée DWH ↔ Power BI Cloud | Power BI, PostgreSQL |

---

## 4. Résumé des changements

### 4.1 Définition de la complexité
- **SIMPLE** : changement mineur, faible impact, développement rapide
- **MOYEN** : développement structuré, tests dédiés, coordination limitée
- **COMPLEXE** : plusieurs composants, impacts forts, risques techniques élevés

### 4.2 Tableau des changements

| Plateforme | Description du changement | Complexité | Commentaires |
|------------|---------------------------|------------|--------------|
| Odoo | Mise en place d'une réplica read-only | MOYEN | Évite d'impacter la prod |
| ETL | Pipeline Spark + Airflow (extraction, transformation, chargement) | COMPLEXE | Cœur du projet |
| DWH | Modélisation en étoile + data marts sur PostgreSQL | COMPLEXE | Modèle à valider métier |
| Power BI | Dashboards + datasets + RLS | MOYEN | Itératif selon retours |
| Sécurité | SSO Entra ID + gestion des accès | MOYEN | RLS dynamique |
| Migration | Reprise des données legacy | COMPLEXE | Volume et qualité à évaluer |
| DevOps | Dockerisation Airflow + Spark, environnements | MOYEN | Parité DEV/PROD |

---

## 5. Liste des fonctionnalités attendues

### 5.1 Définition des priorités
- **HAUTE** : critique, indispensable
- **MOYENNE** : importante, valeur ajoutée
- **BASSE** : optionnelle ou ultérieure

### 5.2 Tableau des fonctionnalités

| ID | Fonctionnalité | Description | Priorité | Commentaires |
|----|----------------|-------------|----------|--------------|
| TF-01 | Extraction Odoo | Extraction incrémentale des tables métier Odoo | HAUTE | Réplica read-only, watermark |
| TF-02 | Reprise données legacy | Chargement initial des données historiques | HAUTE | One-shot + contrôles |
| TF-03 | Transformation & modélisation DWH | Modèle en étoile (faits + dimensions) | HAUTE | SCD2 sur dimensions clés |
| TF-04 | Data marts métier | Vues agrégées par domaine | HAUTE | Alimente Power BI |
| TF-05 | Orchestration ETL | Planification Airflow + alerting | HAUTE | DAGs, retries |
| TF-06 | Dashboards Power BI | Dashboards interactifs par domaine | MOYENNE | Itératif |
| TF-07 | Authentification SSO | Entra ID pour l'accès aux dashboards | HAUTE | SSO natif Power BI |
| TF-08 | Contrôle d'accès par audience | Segmentation des rapports (App audiences) | MOYENNE | Groupes Entra ID |
| TF-09 | Sécurité niveau ligne (RLS) | Filtrage dynamique par utilisateur/région | HAUTE | `USERPRINCIPALNAME()` |
| TF-10 | Historisation (SCD2) | Suivi des changements sur dimensions | MOYENNE | Clients, produits |
| TF-11 | Monitoring & alerting | Supervision ETL, DWH, Power BI | HAUTE | Airflow UI + ELK |
| TF-12 | Documentation & data catalog | Dictionnaire de données, mapping | BASSE | Itératif |

---

## 6. Détails techniques de développement des fonctionnalités

### 6.1 Fonctionnalité : Extraction Odoo (TF-01)

#### 6.1.1 Description technique
- **Source** : réplica PostgreSQL d'Odoo (read-only)
- **Mode** : incrémental basé sur `write_date` / `create_date`
- **Tables ciblées** : `sale_order`, `purchase_order`, `account_move`, `res_partner`, `product_product`
- **Composants** : Airflow (déclenchement) → Spark (extraction) → PostgreSQL staging
- **Contraintes** :
  - Jamais de requête sur la base Odoo de production
  - Watermark stocké dans une table de contrôle
  - Batch size : 10 000 lignes
  - Retry : 3 tentatives avec backoff exponentiel

#### 6.1.2 Diagramme de séquence

```
Airflow → Spark : déclenche job extraction
Spark → Réplica Odoo : SELECT ... WHERE write_date > watermark
Réplica Odoo → Spark : lignes extraites
Spark → PostgreSQL (staging) : INSERT lignes brutes
Spark → Table contrôle : UPDATE watermark
Spark → Airflow : statut OK / KO
Airflow → Monitoring : log + alerte si KO
```

### 6.2 Fonctionnalité : Transformation & modélisation DWH (TF-03)

#### 6.2.1 Description technique
- **Modèle en étoile** :
  - Faits : `fact_ventes`, `fact_achats`, `fact_ecritures_comptables`
  - Dimensions : `dim_temps`, `dim_client`, `dim_produit`, `dim_fournisseur`, `dim_societe`
- **Transformations** : nettoyage, déduplication, normalisation, mapping legacy, SCD2 sur `dim_client` et `dim_produit`
- **Contraintes** : idempotence des jobs, tests de cohérence (nb lignes source vs cible)

#### 6.2.2 Diagramme de séquence

```
Airflow → Spark : déclenche job transformation
Spark → PostgreSQL (staging) : lit données brutes
Spark → Spark : applique règles de transformation
Spark → PostgreSQL (dwh) : UPSERT / MERGE
Spark → Table contrôle qualité : INSERT résultats
Spark → Airflow : statut + métriques
```

### 6.3 Fonctionnalité : Dashboards Power BI (TF-06)

#### 6.3.1 Description technique
- **Connexion** : Power BI → Data Marts (via gateway)
- **Mode** : Import (performance) ou DirectQuery (fraîcheur)
- **Datasets partagés** par domaine métier
- **Actualisation planifiée** : quotidienne à 03:00 (après ETL)

#### 6.3.2 Diagramme de séquence

```
Utilisateur → Power BI Service : ouvre dashboard
Power BI Service → Gateway : demande données
Gateway → Data Mart (PostgreSQL) : requête SQL
Data Mart → Gateway : résultat
Gateway → Power BI Service : dataset
Power BI Service → Utilisateur : dashboard affiché (RLS appliquée)
```

### 6.4 Fonctionnalité : Authentification SSO (TF-07)

#### 6.4.1 Description technique
- **Fournisseur d'identité** : Microsoft Entra ID (OIDC/OAuth2)
- **Flux** : utilisateur → Entra ID → Power BI Service
- **Configuration** : Power BI tenant configuré pour utiliser Entra ID comme IdP
- **Contrainte** : les utilisateurs doivent avoir une licence Power BI Pro (ou être couverts par Fabric Capacity)

#### 6.4.2 Diagramme de séquence

```
Utilisateur → Power BI Service : accès dashboard
Power BI Service → Entra ID : redirection authentification
Entra ID → Utilisateur : page de login
Utilisateur → Entra ID : credentials
Entra ID → Power BI Service : token + identité
Power BI Service → Utilisateur : accès autorisé
```

### 6.5 Fonctionnalité : Sécurité niveau ligne (TF-09)

#### 6.5.1 Description technique
- **RLS dynamique** basée sur `USERPRINCIPALNAME()`
- **Table de mappage** dans le modèle sémantique : `Users` (UserPrincipalName, Région, Rôle)
- **Filtre DAX** : `[Region] = LOOKUPVALUE('Users'[Region], 'Users'[UserPrincipalName], USERPRINCIPALNAME())`
- **Rôles** : `Manager Régional`, `Manager National`, `Admin`

#### 6.5.2 Diagramme de séquence

```
Utilisateur → Power BI Service : ouvre dashboard
Power BI Service → Power BI Service : évalue RLS avec USERPRINCIPALNAME()
Power BI Service → Data Mart : requête filtrée par région
Data Mart → Power BI Service : données filtrées
Power BI Service → Utilisateur : dashboard filtré
```

*(Répéter pour TF-02, TF-04, TF-05, TF-08, TF-10, TF-11, TF-12)*

---

## 7. Base de données

### 7.1 Schéma de données (simplifié)

```
dim_temps
- id_temps (PK)
- date, jour, mois, trimestre, annee

dim_client
- id_client (PK)
- code_client, nom, region, segment
- valid_from, valid_to (SCD2), is_current

dim_produit
- id_produit (PK)
- code_produit, libelle, categorie
- valid_from, valid_to (SCD2), is_current

fact_ventes
- id_vente (PK)
- id_temps (FK), id_client (FK), id_produit (FK)
- quantite, montant_ht, montant_ttc
- source_system

fact_achats
- id_achat (PK)
- id_temps (FK), id_fournisseur (FK), id_produit (FK)
- quantite, montant_ht
- source_system
```

**Organisation des schémas PostgreSQL :**
- `staging` : données brutes extraites
- `dwh` : modèle en étoile (faits + dimensions)
- `dm` : data marts agrégés

**Index :**
- `fact_ventes(id_temps, id_client, id_produit)`
- `dim_client(code_client, is_current)`
- `dim_produit(code_produit, is_current)`

### 7.2 Requêtes principales

**Chargement d'une vente (job ETL)**
- Tables impactées : `staging.ventes` → `dwh.fact_ventes`
- Logique : déduplication sur `(source_system, source_id)`, résolution des clés de dimension, UPSERT

**Mise à jour SCD2 client**
- Tables impactées : `dwh.dim_client`
- Logique : si attribut modifié → clôture ligne courante (`valid_to = now`, `is_current = false`) + insertion nouvelle ligne

**Alimentation d'un data mart**
- Tables impactées : `dm.ventes_par_region_mois`
- Logique : agrégation depuis `fact_ventes` + `dim_client` + `dim_temps`, rafraîchissement complet

### 7.3 Optimisation
- **Indexation** : clés de jointure, colonnes de filtre (date, région, segment)
- **Partitionnement** : `fact_ventes` et `fact_achats` par année
- **Volumétrie** : à estimer (nb lignes/an, croissance)
- **Archivage** : données > 5 ans vers tables d'archive
- **Maintenance** : VACUUM/ANALYZE après chargements massifs

---

## 8. Configuration

### 8.1 Configuration par plateforme

Les paramètres ci-dessous définissent la configuration de référence. Ils sont externalisés dans des fichiers `.env` ou variables d'environnement, afin d'être adaptés par environnement sans modifier le code.

| Plateforme | Paramètre | Description | Valeur | Commentaire |
|------------|-----------|-------------|--------|-------------|
| Odoo (réplica) | DB_HOST | Hôte du réplica | `odoo-replica` | Read-only |
| Odoo (réplica) | DB_PORT | Port PostgreSQL | `5432` | |
| ETL | BATCH_SIZE | Taille des lots d'extraction | `10000` | Ajustable |
| ETL | RETRY_MAX | Nb de tentatives en cas d'échec | `3` | Backoff exponentiel |
| ETL | SPARK_LOCAL_DIR | Répertoire temporaire Spark | `/tmp/spark` | Dans le conteneur |
| DWH | DB_HOST | Hôte PostgreSQL DWH | `dwh-postgres` | |
| DWH | SCHEMA_STAGING | Schéma des données brutes | `staging` | |
| DWH | SCHEMA_DWH | Schéma du modèle en étoile | `dwh` | |
| DWH | SCHEMA_DM | Schéma des data marts | `dm` | |
| Docker | WSL2_BACKEND | Backend Docker Desktop | `true` | Obligatoire sur Windows |
| Docker | MEMORY_LIMIT | Mémoire allouée à Docker | `8GB` | Recommandé pour Spark |
| Docker | VOLUME_BASE_PATH | Chemin des volumes persistants | `\\wsl$\Ubuntu\home\...` | Éviter `C:\` |
| Airflow | DAG_VOLUME | Volume des DAGs | `/opt/airflow/dags` | Persistant |
| Power BI | REFRESH_SCHEDULE | Fréquence de rafraîchissement | `daily 03:00` | Après ETL |
| Power BI | GATEWAY_MODE | Mode de la gateway | `enterprise` | |
| Sécurité | IDP | Fournisseur d'identité | `Entra ID` | SSO |

### 8.2 Gestion des environnements

| Paramètre | DEV | TEST / QA | UAT | PROD |
|-----------|-----|-----------|-----|------|
| Source Odoo | DB locale / sample | Réplica test | Réplica UAT | Réplica prod |
| Source legacy | Fichiers échantillon | Fichiers complets | Fichiers complets | Fichiers complets |
| DWH | PostgreSQL local (Docker) | PostgreSQL test | PostgreSQL UAT | PostgreSQL prod |
| Airflow | Docker local | Docker (serveur test) | Docker (serveur UAT) | Docker Engine / K8s |
| Spark | Local mode | Standalone | Standalone | Cluster |
| Power BI | Workspace perso | Workspace test | Workspace UAT | Workspace prod |
| Actualisation | Manuelle | Quotidienne | Quotidienne | Quotidienne |
| Log level | DEBUG | INFO | INFO | WARN |

**Parité DEV/PROD** : le même `docker-compose.yml` est utilisé en DEV et en TEST, avec des variables d'environnement différentes (`.env`). La production ne repose pas sur Docker Desktop mais sur Docker Engine (Linux) ou Kubernetes.

---

## 9. Monitoring et reporting

### 9.1 Monitoring

#### 9.1.1 Sources des logs

| Source | Type de logs | Description | Fréquence |
|--------|--------------|-------------|-----------|
| ETL (Spark) | Logs applicatifs | Début/fin job, nb lignes, erreurs, durées | Temps réel |
| Airflow | Logs système | Succès/échec des DAGs, retries | Temps réel |
| DWH (PostgreSQL) | Logs SGBD | Requêtes lentes, erreurs, locks | Temps réel |
| Power BI | Logs d'usage | Connexions, actualisations, erreurs | Temps réel |
| Sécurité | Logs de sécurité | Accès aux données, RLS, authentification | Temps réel |

#### 9.1.2 Configuration du monitoring
- **Orchestrateur** : Airflow UI (état des DAGs, logs, durées)
- **Logs centralisés** : ELK (Elasticsearch / Logstash / Kibana) — optionnel en v1
- **Métriques infra** : Prometheus + Grafana — optionnel en v1
- **Alerting** : email + Teams
- **Rétention** : logs ETL 90 jours ; logs sécurité 1 an
- **Seuils d'alerte** :
  - Échec d'un job ETL critique → alerte immédiate
  - Retard de chargement > 2h → alerte
  - Actualisation Power BI en échec → alerte
  - Requête DWH > 30 s → alerte perf

#### 9.1.3 Indicateurs à suivre

| Indicateur | Description | Mode de calcul |
|------------|-------------|----------------|
| Taux de succès des jobs ETL | % jobs réussis | Nb jobs OK / Nb jobs total |
| Fraîcheur des données | Délai entre source et DWH | timestamp DWH - timestamp source |
| Durée moyenne des jobs | Performance ETL | Somme durées / Nb jobs |
| Taux d'échec actualisation PBI | % refresh Power BI en échec | Nb refresh KO / Nb refresh total |
| Disponibilité DWH | Taux de dispo du DWH | (Temps total - indispo) / Temps total |

### 9.2 Reporting

#### 9.2.1 Sources des données

| Source | Description | Fréquence de mise à jour |
|--------|-------------|--------------------------|
| Data marts DWH | Données agrégées prêtes pour Power BI | Quotidienne |
| Logs ETL | Suivi de la qualité des chargements | Temps réel / Batch |
| Power BI Service | Métriques d'usage des dashboards | Quotidienne |

#### 9.2.2 Indicateurs de reporting

| Indicateur | Description | Mode de calcul | Format |
|------------|-------------|----------------|--------|
| Volumétrie chargée | Nb lignes chargées par job | Comptage par run | Dashboard |
| Taux de complétude | % enregistrements complets | Nb complets / Nb total | Rapport PDF |
| Respect du SLA de fraîcheur | Données dispo avant heure cible | Nb runs OK / Nb runs | Export Excel |
| Usage des dashboards | Nb consultations par dashboard | Comptage Power BI | Dashboard |

#### 9.2.3 Format de restitution
- Dashboards interactifs Power BI (par domaine métier)
- Rapports paginés PDF
- Exports Excel / CSV
- Dataset partagé accessible via API Power BI

---

## Annexes

### A. Mapping legacy → Odoo → DWH
Tableau de correspondance : `champ source legacy | champ Odoo | champ DWH | transformation | règle de gestion`

### B. Dictionnaire de données
Tables, colonnes, types, descriptions, contraintes.

### C. Règles de gestion métier
Calculs (CA, TVA, devises), arrondis, gestion des avoirs, etc.

### D. Contrôles qualité
Liste des tests automatiques : unicité, complétude, cohérence, réconciliation source/cible.

### E. Plan de double run / réconciliation
Période de double exécution legacy + Odoo, comparaison des résultats, critères de bascule.

### F. Journal des décisions (decision log)
| Décision | Alternatives | Justification |
|----------|--------------|---------------|
| Spark + Airflow | dbt, Talend | Traitement distribué, orchestration UI, open source |
| PostgreSQL (DWH) | Microsoft Fabric | Coût, simplicité, pas de lock-in |
| Docker (DEV) | Installation native | Reproductibilité, parité DEV/PROD |
| SSO Entra ID | Auth locale | Intégration native Power BI |
| RLS dynamique | RLS statique | Maintenabilité, scalabilité |

---

Voilà **à quoi ressemblera ta spec finale**. Elle est complète, cohérente, et couvre tous les aspects que tu as mentionnés : Spark, Airflow, Docker, PostgreSQL, Power BI, SSO, RLS, monitoring, migration.

Tu peux t'en servir comme **modèle direct** : remplace les valeurs par les tiennes, ajuste les fonctionnalités selon ton périmètre réel, et complète les annexes au fur et à mesure. Si tu veux, on peut maintenant travailler sur **une section en particulier** (par exemple l'annexe A mapping, ou le scénario de démo) pour que tu aies un livrable encore plus concret. 🙂