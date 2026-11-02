# Objectif du document 
Cette spécification technique couvre la chaîne data de bout en bout du module de Reporting et Dashboard : des l'ingestion des données sources (Odoo) jusqu'à la restitution via l'application Power BI, en incluant les aspects de sécurité (SSO, RLS). Elle s'inscrit dans le cadre de la migration Qualipro vers Odoo. 
- Périmètre inclus : ETL (Spark + Airflow), Datawarehouse (PostgreSQL), Data Marts, Reporting Power BI, Authentification SSO, contrôle d'accès, environnements, monitoring. 

---
## 1. Historique du document 

| Version | Date       | Rédacteur | Commentaire            |
| ------- | ---------- | --------- | ---------------------- |
| 0.1     | JJ/MM/AAAA | Laura     | Création initiale      |
| 0.2     | JJ/MM/AAAA | Laura     | Ajustements techniques |
| 1.0     | JJ/MM/AAAA | Laura     | Version validée        |
## 2. Validation du document 

|                | Nom | Fonction | Signature | Date |
| -------------- | --- | -------- | --------- | ---- |
| Référent IT    |     |          |           |      |
| Responsable IT |     |          |           |      |
## 3. Architecture globale 
### 3.1 Diagramme d'architecture 
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
### 3.2 Description des composants 

| Composant                 | Type          | Description / Rôle                               | Interfaces / Liaisons |
| ------------------------- | ------------- | ------------------------------------------------ | --------------------- |
| Odoo (Réplica PostgreSQL) | Source        | Base transactionnelle en lecture seule           | Lecture SQL           |
| Apache Spark              | Service ETL   | Extraction, Transformation, Chargement distribué | Sources, DWH          |
| Apache Airflow            | Orchestrateur | Planification et supervision des jobs ETL        | Spark, monitoring     |
| Docker                    | Middleware    | Conteneurisation Airflow + Spark (DEV / PROD)    | Tous composants       |
| PostgreSQL (DWH)          | SGBD          | Stockage Modelisé (Datawarehouse, Data Marts)    | Spark, Power BI       |
| Power BI                  | Reporting     | Dashboards, RLS                                  | DWH, Entra ID         |
| Microsoft Entra ID        | Sécurité      | SSO, authentification, groupes                   | Power BI;             |

## 4. Résumé des changements 
### 4.1 Définition de la complexité 
- SIMPLE : Changement mineur, faible impact, développement rapide, peu ou pas de dépendances 
- MOYEN : Changement nécessitant un développement structuré, tests dédiés et coordination limitée
- COMPLEXE : Changement majeur impliquant plusieurs composants, impacts forts, risques techniques élevés 
### 4.2 Tableau des changements 

| Plateforme    | Description du changement                                                | Complexité | Commentaires                                   |
| ------------- | ------------------------------------------------------------------------ | ---------- | ---------------------------------------------- |
| Odoo (source) | Mise en place d'une réplica read-only pour l'ETL                         | MOYEN      | Evite d'impacter l'environnement de production |
| ETL           | Pipeline Spark + Airflow (extraction, transformation, chargement)        | COMPLEXE   | Coeur du projet                                |
| Datawarehouse | Création du modèle en étoile + data marts                                | COMPLEXE   | Modèle à valider                               |
| Power BI      | Création des dashboards                                                  | MOYEN      | Itératif selon retours                         |
| Sécurité      | Gestion des accès Power BI (SSO Entra ID); authentification utilisateurs | MOYEN      | RLS (Row Level Security) dynamique             |
## 5. Liste des fonctionnalités attendues 
### 5.1 Définition des priorités 
- HAUTE : Fonctionnalité critique indispensable au fonctionnement de la solution
- MOYENNE : Fonctionnalité importante apportant une valeur ajoutée significative 
- BASSE : Fonctionnalité optionnelle ou d'amélioration ultérieure 
### 5.2 Tableau des fonctionnalités 

| ID    | Fonctionnalité                     | Description                                                | Priorité | Commentaires                            |
| ----- | ---------------------------------- | ---------------------------------------------------------- | -------- | --------------------------------------- |
| TF-01 | Extraction Odoo                    | Extraction incrémentale des tables métier Odoo             | HAUTE    | Réplica read-only de la base de données |
| TF-02 | Transformations & modélisation DWH | Modèle en étoile (faits + dimensions)                      | HAUTE    |                                         |
| TF-03 | Data marts métier                  | Vues agrégées par domaine                                  | HAUTE    | Alimente les dashboards Power BI        |
| TF-04 | Orchestration ETL                  | Planification des jobs ETL, alertes en cas d'échec         | HAUTE    | Via Apache Airflow                      |
| TF-05 | Dashboard Power BI                 | Dashboard interactifs par module / domaine                 | MOYENNE  | Itératif                                |
| TF-06 | Authentification SSO               | Intégration Microsoft Entra ID pour l'accès aux dashboards | MOYENNE  |                                         |
| TF-07 | Sécurité & RLS                     | Row-Level Security dans Power BI                           | MOYENNE  | Par rôle / périmètre                    |
| TF-08 | Historisation (SCD)                | Suivi des changements sur les dimensions clés              | MOYENNE  |                                         |
| TF-09 | Monitoring & alerting              | Supervision ETL, DWH, Power BI                             | MOYENNE  |                                         |

## 6. Détails techniques de développement des fonctionnalités 
Une sous section doit être créée pour chaque fonctionnalité technique 
### 6.1 Fonctionnalité : Extraction Odoo (TF-01)
#### 6.1.1 Description technique 
- **Source :** réplica PostgreSQL d'Odoo (read-only)
- **Mode :** incrémental
- **Tables ciblées :** 
- **Composants :** Airflow (déclenchement) → Spark (extraction) → PostgreSQL staging
- **Contraintes :** 
	- Ne jamais effectuer de requête sur la base de production 
	- Batch size : 5000 lignes
	- Retry : 3 tentatives 
#### 6.1.2 Diagramme de séquence 
	Airflow → Spark : déclenche job extraction
	Spark → Réplica Odoo : SELECT ... WHERE write_date > watermark
	Réplica Odoo → Spark : lignes extraites
	Spark → PostgreSQL (staging) : INSERT lignes brutes
	Spark → Table contrôle : UPDATE watermark
	Spark → Airflow : statut OK / KO
	Airflow → Monitoring : log + alerte si KO

![[TF-01.png]]

Ce diagramme illustre le pipeline d'extraction incrémentale orchestré par Apache Airflow. Airflow déclenche le job d'extraction de Spark, qui va interroger la réplica d'Odoo en filtrant les enregistrements selon un watermark (WHERE write_date > watermark) afin de ne récupérer que les données nouvelles ou modifiées depuis la dernière exécution. 

Les lignes extraites sont ensuite insérées brutes dans un schéma staging PostgreSQL, puis Spark va mettre à jour la table de contrôle contenant le watermark pour garantir l'idempotence et éviter les doublons lors des prochains runs. Enfin, Spark remonte un statut (OK / KO) à Airflow, qui journalise l'exécution et déclenche une alerte en cas d'échec via le monitoring. 

La fiabilité du watermak et la gestion des erreurs (status KO) sont critiques pour éviter les pertes ou reprises de données. 
### 6.2 Fonctionnalité : Transformation & modélisation DWH (TF-03)
#### 6.2.1 Description technique 
- **Modèle en étoile :** 
	- **Faits :** 
	- **Dimensions :** 
- **Transformations :** nettoyage, déduplication, normalisation, résolution des clés de dimension
- **Contraintes :** 
	- Tests de cohérence (nb lignes sources vs cible)
	- Idempotence des jobs (rejouables sans doublons)
	- Gestion des SCD (voir TF-08)
#### 6.2.2 Diagramme de séquence 
	Airflow → Spark : déclenche job transformation
	Spark → PostgreSQL (staging) : lit données brutes
	Spark → Spark : applique règles de transformation
	Spark → PostgreSQL (dwh) : UPSERT / MERGE
	Spark → Table contrôle qualité : INSERT résultats
	Spark → Airflow : statut + métriques

![[TF-02.png]]

Ce diagramme décrit le pipele de transformation orchestré par Airflow. Airflow déclenche le job transformation de Spark, qui effectue ensuite la lecture des données brutes depuis le schéma staging PostgreSQL, puis applique les règles de transformations (nettoyage, normalisation, déduplication,...) définies. Les données transformées sont ensuite chargées dans le schéma datawarehouse PostgreSQL via un `UPSERT / MERGE`, garantissant l'idempotence et la mise à jour des enregistrements existants sans doublons. 

Spark insère parallèlement les résultats des contrôles qualité dans une table dédiée, puis remonte à Airflow le statut d'exécution ainsi que les métriques associées (volumes traités, rejets, durée). Point d'attention : il faut garantir que les lignes rejetées par le contrôle qualité ne soient pas chargées dans le DWH (ou soient marquées), afin d'éviter d'exposer des données non fiables en aval.
### 6.3 Fonctionnalité : Data Marts métier (TF-03)
#### 6.3.1 Description technique 
- Objectif : Mettre en place des vues agrégées par domaine métier, prête à être consommées par Power BI
- Data marts cibles (v1) : 
	- dm_indicateurs : 
- Composants : Spark (agrégation) → PostgreSQL schéma → Power BI
- Contraintes : 
	- Une vue = un besoin métier identifié 
	- Colonnes nommées de façon métier 
	- Documentation dans un dictionnaire de données
#### 6.3.2 Diagramme de séquence 
	Airflow → Spark : déclenche job data marts
	Spark → PostgreSQL (dwh) : lit faits + dimensions
	Spark → Spark : agrège par domaine métier
	Spark → PostgreSQL (dm) : TRUNCATE + INSERT (full refresh)
	Spark → Table contrôle qualité : INSERT volumétrie
	Spark → Airflow : statut

![[TF-03.png]]
Ce diagramme décrit le pipeline de construction des datamarts orchestrés par Airflow. Airflow met en marche le job data mart de Spark, qui lit les tables de faits et de dimensions depuis le datawarehouse PostgreSQL, puis agrès les données par domaine métier pour produire des tables adaptées aux besoins décisionnels. Les résultats sont chargés dans les datamarts via un `TRUNCATE` + `INSERT` (raifraîchissement complet), stratégie simple qui garantit que le mart reflète exactement les données du datawarehouse au moment du run. 

Spark insère ensuite la volumétrie produite dans la table de contrôle qualité, puis remonte le statut d'éxécution vers Airflow. Point d'attention : le `TRUNCATE` + `INSERT` rend le mart indisponible ou partiellement vide pendant le rechargement; il faut donc assurer que les consommateurs en aval ne lisent pas le mart durant cette fenêtre de rechargements ou prévoir un chargement dans une table temporaire puis un `swap`.
### 6.4 Fonctionnalité : Mise en place et orchestration ETL (TF-04)
#### 6.4.1 Description technique 
- Orchestrateur : Apache Airflow (conteneurisé via Docker)
- DAGs principaux : 
	- `dag_extract_odoo` : extraction quotidienne (TF-01)
	- `dag_transform_dwh`: transformation et modélisation (TF-02)
	- `dag_build_datamarts`: construction des datamarts (TF-03)
	- `dag_full_pipeline`: enchaînement complet (extract → transform → load)
- Dépendances : 
	- `dag_transform_dwh` dépend de `dag_extract_odoo`
	- `dag_build_datamarts` dépend de `dag_transform_dwh`
- Planification : 
	- Quotidienne à 01:00 (pipeline complet avant le refresh Power BI de 03:00)
- Gestion des erreurs : 
	- Retry automatiques (3 tentatives)
	- Alertes emails en cas d'échec définitif 
	- SLA : alerte si le pipeline n'est pas terminé à 02:30
- Contraintes : 
	- Idempotence : un DAG rejoué ne doit pas créer de doublons 
	- Logs centralisés et consultables via l'UI Airflow
#### 6.4.2 Diagramme de séquence 
	Scheduler Airflow → DAG extract : déclenche à 01:00
	DAG extract → Spark : job extraction
	DAG extract → DAG transform : trigger si succès
	DAG transform → Spark : job transformation
	DAG transform → DAG datamarts : trigger si succès
	DAG datamarts → Spark : job data marts
	DAG datamarts → Airflow : statut final
	Airflow → Monitoring : log + alerte (email/Teams) si KO ou SLA dépassé

![[TF-04 1.png]]
Ce diagramme illustre l'orchestration globale du pipeline via Airflow, sous forme de trois DAGs chaînés. Le scheduler Airflow déclenche le DAG `extract` à 01:00, qui lance le job Spark d'extraction. En cas de succès, `extract` déclence le DAG `transform` (job Spark de transformation), qui à son tour, si sa propre exécution est un succès, déclenche le DAG `datamarts` (job Spark de construction des marts). 

Cette chaîne garantit un enchaînement séquentiel où chaque étape ne démarre que si la précedente a réussi, évitant ainsi de propager des données incomplètes ou erronées. A l'issue du dernier DAG, le statut final est remonté vers Airflow, qui journalise l'exécution et déclenche une alerte en cas d'échec (KO) ou de dépassement du SLA.  

Point d'attention : le déclenchement conditionnel entre DAGs (trigger on success) est le garant de l'intégrité du pipeline ETL; toute défaillance en cours de chaîne doit être visible via le monitoring pour éviter un blocage silencieux. En cas de KO, une statégie de reprise peut être prévue (relance du DAG échouée, reprise depuis le watermark) pour ne pas rejouer tout le pipeline. 
### 6.5 Fonctionnalité : Dashboards Power BI (TF-05)
#### 6.5.1 Description technique 
- **Connexion :** Power BI → Data Marts 
- **Mode :** Import (performance) ou DirectQuery (fraîcheur)
- **Datasets partagés** par domaine métier 
- **Actualisation planifiée :** quotidienne à 03:00 (après ETL)
- Dashboard v1 : 
	- Dashboard Indicateurs 
- Contraintes : 
	- RLS appliquée sur tous les datasets (voir TF-07)
	- Actualisation conditionnée à la réussite du pipeline ETL
	- Documentation des mesures DAX dans le dictionnaire de données
#### 6.5.2 Diagramme de séquence 
	Utilisateur → Power BI Service : ouvre dashboard
	Power BI Service → Gateway : demande données
	Gateway → Data Mart (PostgreSQL) : requête SQL
	Data Mart → Gateway : résultat
	Gateway → Power BI Service : dataset
	Power BI Service → Utilisateur : dashboard affiché (RLS appliquée)

![[TF-05 1.png]]

Ce diagramme décrit le chemin de lecture des données par les utilisateurs finaux via Power BI. L'utilisateur ouvre un dashboard dans Power BI Service, qui demande les données à la passerelle (Gateway). Le Gateway exécute une requête SQL sur le datamart PostgreSQL, récupère le résultat et le transmet à Power BI Service sous forme de dataset, qui affiche alors le dashboard à l'utilisateur. 

La sécurité au niveau des lignes (RLS, Row-Level Security) est appliquée lors de cette restitution : chaque utilisateur ne voit que les données auxquelles son rôle lui donne accès (comme le définit la régle de gestion dans le BRD). 

Point d'attention : le Gateway est un point unique de la chaîne (single point of failure) et la RLS doit être configurée et testée côté Power BI et cohérente avec les droits définis dans le Datamart, sous peine d'exposer des données à un utilisateur non habilité. 
### 6.6 Fonctionnalité : Authentification SSO (TF-06)
#### 6.6.1 Description technique 
- Fournisseur d'identité : Microsoft Entra ID (OIDC/OAuth2)
- Flux : utilisateur → Entra ID ⇾ Power BI Service
- Configuration : Power BI tenant configuré pour utiliser Entra ID
- Contraintes : 
	- Les groupes Entra ID servent de base pour les audiences Power BI (TF-05) et la RLS (TF-07)
	- Aucun compte local Power BI autorisé en production 
#### 6.6.2 Diagramme de séquence 
	Utilisateur → Power BI Service : accès dashboard
	Power BI Service → Entra ID : redirection authentification
	Entra ID → Utilisateur : page de login
	Utilisateur → Entra ID : credentials
	Entra ID → Power BI Service : token + identité
	Power BI Service → Utilisateur : accès autorisé

![[TF-06.png]]

Ce diagramme décrit le flux d'authentification des utilisateurs accédant aux dashboards Power BI. Lorsqu'un utilisateur tente d'accéder à un dashboard, Power BI Service le redirige vers Entra ID pour l'authentification. Entra ID affiche la page de login, l'utilisateur saisit ses identifiants, puis Entra ID valide l'authentification et renvoie à Power BI Service un token accompagné de l'identité de l'utilisateur; c'est l'identité du token qui détermine les données qui seront visible à l'utilisateur. Power BI Service autorise alors l'accès au dashboard. 

Ce mécanisme repose sur une authentification délégué (OIDC) : Power BI ne gère pas les mots de passe, il fait confiance à Entra ID comme fournisseur d'identité. 

Point d'attention : l'identité renvoyée par Entra ID est celle utilisée pour appliquer la RLS; toute incohérence entre les comptes Entra ID et les règles d'accès définies dans Power BI (ou dans le Datamart) peut entraîner un refus d'accès légitime ou, à l'inverse, un accès non autorisé. 
### 6.7 Fonctionnalité : Mise en place RLS (TF-07)
#### 6.7.1 Description technique 
- RLS dynamique basée sur `USERPRINCIPALNAME()`
- Table de mappage dans le modèle sémantique : `Users
	- Colonnes : 
- Filtre DAX : 
- Rôles : 
- Contraintes : 
	- La table `Users` doit être maintenue 
	- Tests RLS obligatoires avant mise en production
	- Documentation des rôles dans le dictionnaire de données
#### 6.7.2 Diagramme de séquence 
	Utilisateur → Power BI Service : ouvre dashboard
	Power BI Service → Power BI Service : évalue RLS
	Power BI Service → Data Mart : requête filtrée
	Data Mart → Power BI Service : données filtrées
	Power BI Service → Utilisateur : dashboard filtré

![[TF-07.png]]

Ce diagramme décrit l'application de la sécurité au niveau ligne (RLS) lors de la consultation d'un dashboard. Lorsque l'utilisateur ouvre le dashboard, Power BI Service évalue les règles RLS en fonction de l'identité de l'utilisateur (voir TF-06), puis génère une requête filtrée vers le Datamart : seule les lignes autorisées sont demandées. Le Datamart renvoie les données filtrées, que Power BI Service restitue à l'utilisateur sous forme de dashboard ne contenant que les données auxquelles il a droit. 

Ce mécanisme garantit que le filtrage est appliqué de bout en bout, et pas seulement côté interface. 

**Point d'attention** : la RLS doit être définie et testée pour chaque rôle ; un rôle mal configuré ou un utilisateur sans rôle associé peut soit voir trop de données, soit se retrouver avec un dashboard vide. Il est recommandé de vérifier la correspondance entre les identités Entra ID et les règles RLS, et de tester avec des comptes représentatifs de chaque profil.
### 6.8 Fonctionnalité : Historisation SDC (TF-08)
#### 6.8.1 Description technique 
- Type : SCD Type 2 (suivi des changements sur dimensions clés)
- Dimensions concernées (v1) :
- Mécanisme : 
	- Colonnes ajoutées : 
	- Si un attribut change : 
- Composants : Spark (détection des changements) → PostgreSQL (dwh)
- Contraintes : 
	- Attributs suivis documentés par dimension 
	- Tests : ...
#### 6.8.2 Diagramme de séquence 
	Airflow → Spark : déclenche job SCD2
	Spark → PostgreSQL (staging) : lit données
	Spark → PostgreSQL (dwh) : SELECT version courante (is_current = true)
	Spark → Spark : compare attributs suivis
	Alt attribut modifié
	    Spark → PostgreSQL (dwh) : UPDATE ligne courante (valid_to, is_current=false)
	    Spark → PostgreSQL (dwh) : INSERT nouvelle ligne (valid_from, is_current=true)
	Else attribut inchangé
	    Spark → Spark : aucune action
	End
	Spark → Airflow : statut + nb changements détectés

![[TF-08.png]]

Ce diagramme décrit le pipeline de gestion de l'historique des données en dimension (SCD de type 2) orchestré par Airflow. Airflow déclenche le job Spark, qui lit les données depuis la zone de staging PostgreSQL, puis récupère dans le Datawarehouse la version courante de chaque enregistrement (is_current = true) afin de la comparer aux attributs suivis (ceux dont l'évolution doit être historisée). 

Si un attribut suivi a changé, Spark clôture la version courante (valid_to, is_current = false) puis insère une nouvelle ligne avec valid_from et is_current = true ; si rien n'a changé, aucune action n'est effectuée. À l'issue du traitement, Spark remonte à Airflow le statut ainsi que le nombre de changements détectés.

Point d'attention : la comparaison doit porter uniquement sur les attributs suivis, et la clôture + insertion doivent être réalisées dans une même transaction (ou un même MERGE atomique) pour éviter d'avoir deux versions courantes simultanément en cas d'échec au milieu du traitement.
### 6.9 Fonctionnalité : Monitoring et alertes (TF-09)
#### 6.9.1 Description technique 
- Objectif : superviser l'ensemble de la chaîne data (ETL, DWH, Power BI) et alerter en cas d'anomalie
- Sources des logs : 
	- Airflow : logs des DAGs 
	- Spark : logs driver + executors 
	- PostgreSQL : logs SGBD (requêtes lentes, erreurs)
	- Power BI : logs d'actualisation et d'usage 
- **Outils (v1) :**
    - Airflow UI (supervision des DAGs)
    - Logs Spark centralisés dans un volume partagé
    - Alertes email + Teams sur échec de DAG ou SLA dépassé
- **Outils (v2, optionnel) :**
    - ELK (Elasticsearch / Logstash / Kibana) pour centralisation des logs
    - Prometheus + Grafana pour métriques infra
- **Seuils d'alerte (v1) :**
    - Échec d'un DAG critique → alerte immédiate
    - Pipeline non terminé à 02:30 → alerte SLA
    - Actualisation Power BI en échec → alerte
- **Rétention :** logs ETL 90 jours ; logs sécurité 1 an
#### 6.9.2 Diagramme de séquence 
Insérer ici le diagramme de séquence décrivant les interactions 
(Format recommandé : UML - diagramme de séquence)
## 7. Base de données 
### 7.1 Schéma de données 
Le Data Warehouse est organisé en trois schémas PostgreSQL distincts correspondants aux trois couches de la chaîne data : 
- `staging` : données brutes extraites d'Odoo, sans transformation (zone d'atterissage)
- **`dwh`** : modèle en étoile (tables de faits + dimensions)
- **`dm`** : data marts agrégés, prêts pour Power BI
#### 7.1.1 Modèle en étoile (schéma `dwh`)
- Table des faits 
- Dimensions 
#### 7.1.2 Schéma `staging`
Le schéma `staging` contient une copie brute des tables Odoo extraites, avec les mêmes colonnes que la source + trois colonnes techniques :
#### 7.1.3 Schéma `dm` (data marts)

#### 7.1.4 ERD simplifié 
	erDiagram
	    DIM_INDICATEUR ||--o{ FAIT_RESULTAT_INDICATEUR : "est mesuré par"
	    DIM_PROCESSUS ||--o{ FAIT_RESULTAT_INDICATEUR : "concerne"
	    DIM_ACTEUR ||--o{ FAIT_RESULTAT_INDICATEUR : "est saisi par"
	    DIM_TEMPS ||--o{ FAIT_RESULTAT_INDICATEUR : "se produit à"
	    DIM_TYPE_INDICATEUR ||--o{ DIM_INDICATEUR : "catégorise"
	
	    FAIT_RESULTAT_INDICATEUR {
	        int id_resultat PK
	        int id_indicateur FK
	        int id_processus FK
	        int id_acteur FK
	        int id_temps FK
	        decimal valeur_saisie
	        decimal objectif_cible
	        decimal taux_atteinte
	        string statut_atteinte
	        string statut_suivi
	        string statut_cloture
	        datetime date_saisie
	        datetime date_maj
	    }
	
	    DIM_INDICATEUR {
	        int id_indicateur PK
	        string numero_indicateur
	        string libelle
	        string description
	        int id_type_indicateur FK
	        string mode_calcul
	        date date_debut
	        date date_fin
	    }
	
	    DIM_TYPE_INDICATEUR {
	        int id_type_indicateur PK
	        string type_indicateur
	        string categorie
	    }
	
	    DIM_PROCESSUS {
	        int id_processus PK
	        string processus
	        string responsable_qualite
	    }
	
	    DIM_ACTEUR {
	        int id_acteur PK
	        string nom
	        string role
	    }
	
	    DIM_TEMPS {
	        int id_temps PK
	        date date
	        string periode
	        string periodicite
	        int annee
	    }
### 7.2 Requêtes principales 
- Chargement : 
- Mise à jour SCD
- Alimentation d'un data mart 
	- Tables impactées : 
	- Logique : 
### 7.3 Optimisation 
#### 7.3.1 Indexation 
- **Index sur les clés étrangères** (indispensables pour les jointures) :
- **Index sur les colonnes de filtre** (utilisées par Power BI) :
- **Index partiel sur SCD2** (garantit l'unicité de la version courante) :
- **Index sur les clés métier** (pour les lookups ETL) :
#### 7.3.2 Optimisation des requêtes
- **`EXPLAIN ANALYZE`** systématique sur les requêtes ETL avant mise en production
- **`VACUUM ANALYZE`** après chaque chargement massif (met à jour les statistiques)
- **`work_mem`** augmenté pour les jobs ETL (tri et hash joins)
- **Requêtes Power BI** : privilégier des agrégations dans les data marts plutôt que des calculs à la volée
#### 7.3.3 Gestion des volumes
- **Volumétrie estimée (à ajuster)** :
- **Partitionnement** (si volumétrie > 1M lignes) :
- **Croissance attendue** : à réévaluer après 6 mois de production.
#### 7.3.4 Stratégie d'archivage
- **Données > 5 ans** : archivées dans des tables `*_archive` (même structure)
- **Données > 7 ans** : exportées en Parquet sur stockage froid, puis supprimées
- **Staging** : purgé après 30 jours (les données brutes n'ont pas besoin d'être conservées longtemps)
- **Logs ETL** : 90 jours (cf. section 9.1.2)
#### 7.3.5 Sauvegarde
- **Sauvegarde complète** : quotidienne (pg_dump) après le pipeline ETL
- **Sauvegarde WAL** : continue (pour la PITR — Point-In-Time Recovery)
- **Rétention** : 30 jours de sauvegardes complètes
- **Test de restauration** : trimestriel

- Indexation : sur les clés de jointure et colonne de filtre (date,...)
- Partitionnement : 
- Gestion des volumes : à estimer (nb lignes / an, croissance)
- Stratégie d'archivage : données > 5 ans vers tables d'archive ou stockage froind
## 8. Configuration 
### 8.1 Configuration par plateforme 

| Plateforme     | Paramètre       | Description                     | Valeur           | Commentaire             |
| -------------- | --------------- | ------------------------------- | ---------------- | ----------------------- |
| Odoo (réplica) | DB_HOST         | Hôte du réplica                 | ``odoo-replica`` | Read-only               |
| Odoo (réplica) | DB_PORT         | Port PostgreSQL                 | ``5432``         |                         |
| ETL            | BATCH_SIZE      | Taille des lots d'extraction    | `10000`          | Ajustable               |
| ETL            | RETRY_MAX       | Nb de tentatives en cas d'échec | `3`              | Backoff exponentiel     |
| ETL            | SPARK_LOCAL_DIR | Répertoire temporaire Spark     | `/tmp/spark`     | Dans le conteneur       |
| DWH            | DB_HOST         | Hôte PostgreSQL DWH             | `dwh-postgres`   |                         |
| DWH            | SCHEMA_STAGING  | Schéma des données brutes       | `staging`        |                         |
| DWH            | SCHEMA_DWH      | Schéma du modèle en étoile      | `dwh`            |                         |
| DWH            | SCHEMA_DM       | Schéma des data marts           | `dm`             |                         |
| Docker         | WSL2_BACKEND    | Backend Docker Desktop          | `true`           | Obligatoire sur Windows |
### 8.2 Gestion des environnements 

| Paramètre     | DEV                       | TEST / QA             | UAT                  | PROD                |
| ------------- | ------------------------- | --------------------- | -------------------- | ------------------- |
| Source Odoo   | DB locale / sample        | Réplica test          | Réplica UAT          | Réplica prod        |
| DWH           | PostgreSQL local (Docker) | PostgreSQL test       | PostgreSQL UAT       | PostgreSQL prod     |
| Airflow       | Docker local              | Docker (serveur test) | Docker (serveur UAT) | Docker Engine / K8s |
| Spark         | Local mode                | Standalone            | Standalone           | Cluster             |
| Power BI      | Workspace perso           | Workspace test        | Workspace UAT        | Workspace prod      |
| Actualisation | Manuelle                  | Quotidienne           | Quotidienne          | Quotidienne         |
| Log level     | DEBUG                     | INFO                  | INFO                 | WARN                |
## 9. Monitoring et reporting 
### 9.1 Monitoring 
#### 9.1.1 Sources des logs

| Source        | Type de logs     | Description                                    | Fréquence  |
| ------------- | ---------------- | ---------------------------------------------- | ---------- |
| ETL           | Logs applicatifs | Début / fin job, nb lignes, erreurs, durées    | Temps réel |
| Orchestrateur | Logs système     | Succès / échec des DAGs, retries               | Temps réel |
| DWH           | Logs SGBD        | Requêtes lentes, erreurs, locks                | Temps réel |
| Power BI      | Logs d'usage     | Connexions, actualisations, erreurs de refresh | Temps réel |
| Sécurité      | Logs de sécurité | Accès aux données, RLS, authentification       | Temps réel |

#### 9.1.2 Configuration du monitoring 
- Outils : 
	- Orchestrateur : Apache Airflow 
	- Logs centralisés : 
	- Métriques : 
	- Canaux de notifications : email
- Rétention : 
	- Logs ETL : 90 jours 
	- Logs sécurité : 1 an
- Seuils d'alerte : 
	- Echec d'un job ETL critique → alerte immédiate
	- Retard de chargement > 2h → alerte
	- Actualisation Power BI en échec → alerte
	- Requête DWH > 45s → alerte performance
#### 9.1.3 Indicateurs à suivre

| Indicateur                          | Description                 | Mode de calcul                   |
| ----------------------------------- | --------------------------- | -------------------------------- |
| Taux de succès des jobs ETL         | % jobs réussis              | Nb jobs OK / Nb jobs total       |
| Fraîcheur des données               | Délai entre source et DWH   | Timestamp DWH - Timestamp source |
| Durée moyenne des jobs              | Performance ETL             | Somme durées / Nb jobs           |
| Taux d'échec actualisation Power BI | % refresh Power BI en échec | Nb refresh KO / Nb refresh total |

### 9.2 Reporting 
#### 9.2.1 Sources des données 

| Source           | Description                           | Fréquence de mise à jour |
| ---------------- | ------------------------------------- | ------------------------ |
| Data marts DWH   | Données agrégées prêtes pour Power BI | Quotidienne              |
| Logs ETL         | Suivi de la qualité des chargements   | Temps réel / Batch       |
| Power BI Service | Métrique d'usage des dashboards       | Quotidienne              |

#### 9.2.2 Indicateurs de reporting

| Indicateur           | Description                    | Mode de calcul         | Format      |
| -------------------- | ------------------------------ | ---------------------- | ----------- |
| Volumétrie chargée   | Nb lignes chargées par job     | Comptage par run       | Dashboard   |
| Taux de complétude   | % enregistrements complets     | Nb complets / Nb total | Rapport PDF |
| Usage des dashboards | Nb consultations par dashboard | Comptage Power BI      | Dashboard   |

#### 9.2.3 Format de restitution
- Dashboards interactifs Power BI (par module)
- Rapport PDF 
- Export Excel / CSV