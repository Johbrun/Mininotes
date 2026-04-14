# MiniNotes

Application web pour gérer ses notes personnelles. Chaque utilisateur
peut s'inscrire, se connecter, et ensuite créer, modifier, supprimer et rechercher
ses propres notes. Il est aussi possible de télécharger une note en fichier texte
et de personnaliser son profil avec un avatar.

L'application est construite en **Python / Flask** avec une base **SQLite** et
des templates **Jinja2**. Le tout tient dans quelques fichiers, sans dépendance
lourde.

## Fonctionnalités

- Inscription et connexion
- Page d'accueil avec la liste de vos notes
- Créer / voir / modifier / supprimer une note
- Rechercher dans vos notes
- Télécharger une note en `.txt`
- Page de profil avec avatar
- Page d'administration (liste des utilisateurs)

## Prérequis

- Python 3.10+ **ou** Docker

## Lancer avec un environnement virtuel (recommandé pour débuter)

```bash
# 1. Créer un environnement virtuel Python
python3 -m venv .venv

# 2. L'activer
#    Sous Linux / macOS :
source .venv/bin/activate
#    Sous Windows (PowerShell) :
#    .venv\Scripts\Activate.ps1

# 3. Installer Flask
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

L'application est alors accessible sur <http://localhost:5000>.

La base de données est créée automatiquement au premier lancement dans
`data/app.db`, avec un utilisateur de démo :

- identifiant : `admin`
- mot de passe : `admin123`

## Lancer avec Docker

```bash
docker compose up --build
```

L'application est accessible sur <http://localhost:5000>. La base de données
et les fichiers uploadés sont conservés dans les dossiers `data/` et `uploads/`
de votre machine.

## Structure du projet

```
minivuln/
├── app.py              # toutes les routes de l'application
├── db.py               # fonctions pour parler à la base SQLite
├── schema.sql          # création des tables
├── requirements.txt    # dépendances Python
├── Dockerfile          # image Docker
├── docker-compose.yml  # lancement Docker
├── templates/          # pages HTML (Jinja)
├── static/             # feuille de style CSS
├── uploads/            # avatars uploadés
└── data/               # base SQLite (créée au premier lancement)
```

## Remise à zéro

Pour repartir d'une base vide :

```bash
rm data/app.db
rm uploads/*
```

La base sera recréée au prochain lancement.
