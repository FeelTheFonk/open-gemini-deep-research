<div align="center">

# GEMINI DEEP RESEARCH

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge&color=3498db" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white&color=2980b9" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&color=f1c40f" />
</p>

<h3><em>L'exploration intelligente à un autre niveau</em></h3>

<p>
<kbd><strong>R</strong>echerche</kbd> • 
<kbd><strong>E</strong>xploration</kbd> • 
<kbd><strong>S</strong>ynthèse</kbd> • 
<kbd><strong>E</strong>xpertise</kbd> • 
<kbd><strong>A</strong>nalyse</kbd> • 
<kbd><strong>R</strong>apport</kbd> • 
<kbd><strong>C</strong>onnaissance</kbd> • 
<kbd><strong>H</strong>olisme</kbd>
</p>

<hr style="height:3px;border:none;color:#333;background-color:#333;margin:30px 0">

</div>

<details close>
<summary><h2>PRINCIPALES FONCTIONNALITÉS</h2></summary>

<table>
  <tr>
    <td align="center"><img src="https://img.shields.io/badge/-recherche_adaptative-informational?style=flat-square&color=3498db"/></td>
    <td><strong>Recherche adaptative</strong><br>Largeur et profondeur ajustables pour une analyse personnalisée</td>
    <td align="center"><img src="https://img.shields.io/badge/-questions_contextuelles-informational?style=flat-square&color=9b59b6"/></td>
    <td><strong>Questions contextuelles</strong><br>Génération intelligente de questions de suivi pour affiner la recherche</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.shields.io/badge/-exploration_arborescente-informational?style=flat-square&color=2ecc71"/></td>
    <td><strong>Exploration arborescente</strong><br>Traitement concurrent de requêtes avec relations parent-enfant</td>
    <td align="center"><img src="https://img.shields.io/badge/-synthèse_narrative-informational?style=flat-square&color=e74c3c"/></td>
    <td><strong>Synthèse narrative</strong><br>Rapports détaillés avec citations, analogies et perspectives multiples</td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.shields.io/badge/-trois_modes-informational?style=flat-square&color=f39c12"/></td>
    <td><strong>Trois modes d'exploration</strong><br>Rapide, équilibré ou exhaustif selon vos besoins</td>
    <td align="center"><img src="https://img.shields.io/badge/-interface_riche-informational?style=flat-square&color=1abc9c"/></td>
    <td><strong>Interface visuelle riche</strong><br>Visualisation en temps réel de la progression et des connexions</td>
  </tr>
</table>

</details>

<details close>
<summary><h2>INSTALLATION</h2></summary>

<table>
  <tr>
    <th align="center" width="50%">Prérequis</th>
    <th align="center" width="50%">Installation rapide</th>
  </tr>
  <tr>
    <td>
      <ul>
        <li>Python 3.12</li>
        <li>Clé API Google Gemini</li>
        <li>Docker (facultatif)</li>
        <li>VS Code avec Dev Containers (facultatif)</li>
      </ul>
    </td>
    <td>
      
```bash
git clone https://github.com/owner/deep_research.git
cd deep_research
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

Créez un fichier `.env` avec votre clé API:
```
GEMINI_KEY=your_api_key_here
```
      
  </tr>
</table>

<details>
<summary>Option alternative: Utilisation du conteneur de développement</summary>
<br>

1. Ouvrez le projet dans VS Code
2. Lorsque vous y êtes invité, cliquez sur "Rouvrir dans un conteneur"
3. Créez un fichier `.env` dans le répertoire racine avec votre clé API Gemini

</details>

</details>

<details close>
<summary><h2>UTILISATION</h2></summary>

<table>

```bash
python main.py "votre requête de recherche"
```

### Exemple

```bash
python main.py "Impact de l'intelligence artificielle sur la santé" --mode comprehensive --num-queries 5
```

Arguments optionnels:
```bash
--mode [fast/balanced/comprehensive]
--num-queries [entier]
--learnings [liste d'apprentissages]
```

---

<p align="center"><i>Interface interactive avec visualisation en temps réel</i></p>

```bash
python ui.py
```

</table>

<div align="center">
  <img src="https://img.shields.io/badge/résultat-3000%2B%20mots%20avec%20citations-success?style=for-the-badge&color=2ecc71" />
</div>

</details>

<details close>
<summary><h2>ARCHITECTURE</h2></summary>

<table>
  <tr>
    <th colspan="2">Modes de recherche</th>
    <th>Structure du projet</th>
  </tr>
  <tr>
    <td width="30%">
      <h4 align="center">Mode rapide [FAST]</h4>
      <ul>
        <li>Recherche de surface</li>
        <li>3 requêtes max</li>
        <li>2-3 questions par requête</li>
        <li>Temps: ~1-3 minutes</li>
      </ul>
    </td>
    <td width="30%">
      <h4 align="center">Mode exhaustif [COMPREHENSIVE]</h4>
      <ul>
        <li>Exploration récursive</li>
        <li>5 requêtes + sous-requêtes</li>
        <li>5-7 questions par requête</li>
        <li>Temps: ~5-12 minutes</li>
      </ul>
    </td>
    <td width="40%">

```
deep_research/
├── .github/              # CI/CD & Workflows
├── src/
│   ├── __init__.py
│   └── deep_research.py  # Moteur principal
├── ui/
│   ├── __init__.py
│   ├── ui_core.py        # Constantes et utilitaires
│   ├── ui_components.py  # Composants d'interface
│   ├── ui_visualizers.py # Visualisations avancées
│   └── ui_workflow.py    # Workflow principal
├── .env                  # Clés API (non suivi)
├── .gitignore
├── main.py               # CLI
├── ui.py                 # Interface Rich
├── README.md
└── requirements.txt      # Dépendances
```
  </tr>
</table>

### Processus de recherche

<div align="center">

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ ANALYSE     │────>│ QUESTIONS   │────>│ RECHERCHE   │
│ REQUÊTE     │     │ DE SUIVI    │     │ CONCURRENTE │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
┌─────────────┐     ┌─────────────┐     ┌──────┴──────┐
│ RAPPORT     │<────│ SYNTHÈSE    │<────│ EXTRACTION  │
│ FINAL       │     │ CONNAISSANCE│     │ DONNÉES     │
└─────────────┘     └─────────────┘     └─────────────┘
```

<p>Flux de recherche multi-couche avec gestion relationnelle des connaissances</p>

</div>

</details>

<details close>
<summary><h2>STRUCTURE DE DONNÉES</h2></summary>

Le cœur du système repose sur une structure d'arbre de recherche sophistiquée :

```json
{
  "query": "requête racine",
  "id": "uuid-1",
  "status": "completed",
  "depth": 2,
  "learnings": ["observation 1", "observation 2"],
  "sub_queries": [
    {
      "query": "sous-requête 1",
      "id": "uuid-2",
      "status": "completed",
      "depth": 1,
      "learnings": ["observation 3"],
      "sub_queries": [],
      "parent_query": "requête racine"
    }
  ],
  "parent_query": null
}
```

<div align="center">
<p>Suivi de progression en temps réel via visualisation arborescente</p>
</div>

</details>

<details close>
<summary><h2>MODULES DE L'INTERFACE</h2></summary>

L'interface utilisateur est maintenant modulaire, organisée en plusieurs composants spécialisés :

### Module `ui_core.py`

- Configuration et constantes de l'application
- Utilitaires fondamentaux et formatage
- Gestion centralisée des traductions

### Module `ui_components.py`

- Composants visuels réutilisables
- Panneaux, tableaux de bord et arbres
- Mise en page et éléments d'interface

### Module `ui_visualizers.py`

- Exportation des rapports (HTML, MD)
- Génération de graphes de connaissances
- Visualisations avancées des données

### Module `ui_workflow.py`

- Processus principal de recherche
- Gestion du cycle de vie des requêtes
- Traitement et génération des rapports

<div align="center">
<p>Architecture modulaire pour une maintenance et une évolutivité optimales</p>
</div>

</details>

<details close>
<summary><h2>VISUALISATIONS</h2></summary>

Le système offre plusieurs types de visualisations pour explorer les résultats :

### Arbre de recherche

Visualisation en temps réel de la structure des requêtes et sous-requêtes avec statuts codés par couleur.

### Graphe de connaissances

Représentation interactive en D3.js des relations entre requêtes, connaissances acquises et sources.

### Rapports narratifs

Génération automatique de rapports structurés avec analogies, citations et perspectives multiples.

### Tableaux de bord de progression

Suivi détaillé de l'avancement avec statistiques sur les requêtes, sources et connaissances.

<div align="center">
<p>Exploration visuelle multiniveau pour une compréhension approfondie</p>
</div>

</details>

<details>
<summary><h2>CONTRIBUTION</h2></summary>

Les contributions sont bienvenues ! Consultez nos issues ouvertes ou proposez des améliorations.

1. Fork le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

</details>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/Explorez-l'inconnu-blueviolet?style=for-the-badge&color=8e44ad" />
  <img src="https://img.shields.io/badge/Connectez-les_connaissances-blueviolet?style=for-the-badge&color=8e44ad" />
  <img src="https://img.shields.io/badge/Découvrez-la_profondeur-blueviolet?style=for-the-badge&color=8e44ad" />

<br><br>

<em>Créé avec passion pour l'exploration intelligente</em>
</div>