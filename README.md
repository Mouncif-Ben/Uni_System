# Uni_System
Système Intelligent d'Optimisation et d'Aide à la Décision pour la Gestion Universitaire
# UniSmart — Système Intelligent de Gestion Universitaire

> Système web d'aide à la décision pour la gestion universitaire, combinant Machine Learning et algorithmes d'optimisation.

---

## Aperçu du projet

UniSmart est une application web académique développée avec **Python Flask** qui intègre deux modules intelligents :

- **Module 1** — Prédiction du risque d'échec étudiant via Machine Learning (Random Forest)
- **Module 2** — Génération automatique d'emploi du temps sans conflits (algorithme Backtracking)

---

## Fonctionnalités

- Dashboard avec indicateurs clés (KPIs)
- Prédiction du risque d'échec des étudiants
- Génération automatique d'emploi du temps
- Gestion des étudiants, professeurs et salles
- Visualisation des statistiques avec graphiques
- Interface web responsive (Bootstrap 5)

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | HTML · CSS · JavaScript · Bootstrap 5 |
| Backend | Python · Flask |
| Base de données | SQLite · Pandas |
| Machine Learning | Scikit-learn · NumPy |
| Visualisation | Seaborn · Matplotlib |
| Outils | Git · GitHub · VS Code |

---

## Structure du projet

```
uni_system/
├── app.py                      # Flask — point d'entrée
├── requirements.txt            # Dépendances Python
├── university.db               # Base de données SQLite
├── .gitignore
│
├── templates/                  # Pages HTML (Jinja2)
│   ├── base.html
│   ├── dashboard.html
│   ├── students.html
│   ├── predictions.html
│   ├── timetable.html
│   ├── rooms.html
│   └── professors.html
│
├── static/                     # CSS et JavaScript
│   ├── css/style.css
│   └── js/main.js
│
├── module1_prediction/         # Module ML
│   ├── __init__.py
│   └── model.py
│
└── module2_timetable/          # Module emploi du temps
    ├── __init__.py
    └── generator.py
```

---

## Installation et lancement

### Prérequis

- Python 3.11+
- Git

### Étapes

**1. Cloner le dépôt**

```bash
git clone https://github.com/VOTRE_USERNAME/uni-smart-system.git
cd uni-smart-system
```

**2. Créer et activer l'environnement virtuel**

```bash
# Créer
python -m venv venv

# Activer — Windows
venv\Scripts\activate

# Activer — Mac / Linux
source venv/bin/activate
```

**3. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**4. Lancer l'application**

```bash
python app.py
```

**5. Ouvrir dans le navigateur**

```
http://localhost:5000
```

---

## Pages de l'application

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/dashboard` | Vue générale avec KPIs et statistiques |
| Etudiants | `/students` | Liste et gestion des étudiants |
| Predictions | `/predictions` | Résultats du modèle ML |
| Emploi du temps | `/timetable` | Grille hebdomadaire générée |
| Salles | `/rooms` | Gestion des salles et laboratoires |
| Professeurs | `/professors` | Liste du corps enseignant |

---

## Module 1 — Prédiction du risque d'échec

**Problème :** Les universités ne détectent les étudiants en difficulté qu'après les examens finaux — trop tard pour intervenir.

**Solution :** Un modèle Random Forest analyse les données disponibles et prédit le risque dès la semaine 3.

**Données utilisées :**
- Note (0–100)
- Taux d'assiduité (%)
- Taux de participation (%)

**Résultat :**
- `at_risk = 1` → étudiant en danger
- `at_risk = 0` → étudiant en sécurité
- Score de risque en pourcentage

**Précision cible :** > 80%

---

## Module 2 — Génération d'emploi du temps

**Problème :** Créer manuellement un emploi du temps sans conflits pour des dizaines de cours, professeurs et salles est impossible.

**Solution :** L'algorithme Backtracking teste chaque assignation et revient en arrière en cas de conflit.

**Contraintes respectées :**
- Un professeur ne peut pas être dans deux salles en même temps
- Une salle ne peut pas avoir deux cours en même temps
- Les cours de laboratoire nécessitent une salle labo
- La capacité des salles ne doit pas être dépassée

---

## Phases du projet

| Phase | Titre | Semaines | Livrable |
|-------|-------|----------|----------|
| Phase 01 | Analyse & Cadrage | S1 – S2 | Cahier des charges |
| Phase 02 | Conception & Architecture | S3 – S4 | UML + Maquettes |
| Phase 03 | Développement | S5 – S8 | Application web |
| Phase 04 | Tests & Validation | S9 – S10 | Rapport de tests |
| Phase 05 | Documentation & Soutenance | S11 – S12 | Rapport final |

---

## Auteur

Projet académique — Système Intelligent de Gestion Universitaire  
Encadré dans le cadre d'un projet de fin d'études.

---

## Licence

Ce projet est développé à des fins académiques uniquement.
