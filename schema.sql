-- Fichier de création des tables de la base de données.
-- Ce fichier est lu automatiquement par db.py au premier lancement
-- de l'application, pour construire la base SQLite vide.

-- Table des utilisateurs.
-- Chaque utilisateur a un identifiant unique (id), un nom d'utilisateur,
-- un mot de passe, un drapeau indiquant si c'est un administrateur,
-- et le chemin vers son avatar (image de profil).
CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT    NOT NULL UNIQUE,
    password  TEXT    NOT NULL,
    is_admin  INTEGER NOT NULL DEFAULT 0,
    avatar    TEXT
);

-- Table des notes.
-- Chaque note appartient à un utilisateur (owner_id), a un titre,
-- un contenu, et une date de création.
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id   INTEGER NOT NULL,
    title      TEXT    NOT NULL,
    content    TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
