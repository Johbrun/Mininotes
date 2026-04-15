"""
Ce fichier regroupe les fonctions pour parler à la base de données SQLite.

SQLite est une base de données stockée dans un simple fichier (data/app.db).
On n'a donc pas besoin d'installer un serveur de base de données séparé.

Pour utiliser la base dans app.py, on appelle :
    - init_db() au démarrage (crée les tables si besoin)
    - get_db() dans une route (renvoie une connexion à la base)
"""

import os
import sqlite3
import hashlib

# Chemin vers le fichier de base de données.
# On le stocke dans le dossier "data/" à côté de app.py.
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")

# Chemin vers le fichier schema.sql qui contient les CREATE TABLE.
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_db():
    """
    Ouvre une connexion à la base SQLite et la renvoie.

    On configure la connexion pour que les résultats soient retournés
    sous forme de "Row" : on peut alors accéder aux colonnes par leur
    nom (row["username"]) plutôt que par leur position (row[0]).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    """
    Transforme un mot de passe en une empreinte (hash) hexadécimale.

    On ne veut pas stocker les mots de passe en clair dans la base :
    on stocke à la place une empreinte calculée à partir du mot de passe.
    """
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def init_db():
    """
    Crée la base de données si elle n'existe pas encore.

    Si le fichier data/app.db n'existe pas, on :
      1. crée le dossier data/ si besoin,
      2. exécute les CREATE TABLE de schema.sql,
      3. insère un utilisateur "admin" de démonstration.
    """
    # 1) S'assurer que le dossier data/ existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Si le fichier existe déjà, on ne refait pas l'initialisation
    if os.path.exists(DB_PATH):
        return

    # 2) Lire le contenu du fichier schema.sql et l'exécuter
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db()
    conn.executescript(schema_sql)

    # 3) Créer un utilisateur "admin" de démonstration
    conn.execute(
        "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
        ("admin", hash_password("admin123"), 1),
    )

    # 4) Lui ajouter une note de bienvenue pour que la home ne soit pas vide
    conn.execute(
        "INSERT INTO notes (owner_id, title, content) VALUES (?, ?, ?)",
        (0, "Bienvenue", "Ceci est une note  qui est privée 🏴‍☠️"),
    )

    conn.commit()
    conn.close()
