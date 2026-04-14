"""
Application MiniNotes.

Ce fichier contient toutes les routes (URL) de l'application.
Une route, c'est une fonction Python associée à une URL :
quand le navigateur demande l'URL, Flask exécute la fonction et
renvoie ce qu'elle retourne au navigateur.

Pour lancer l'application :
    python app.py

Ensuite, ouvrez http://localhost:5000 dans votre navigateur.
"""

import os
from flask import (
    Flask, request, redirect, url_for, render_template,
    session, send_file, abort, make_response,
)

import db


# ---------------------------------------------------------------------------
# Configuration de l'application Flask
# ---------------------------------------------------------------------------

app = Flask(__name__)

# La "secret key" sert à signer les cookies de session.
# Flask l'utilise automatiquement pour que les cookies ne soient pas
# modifiables par le navigateur.
app.secret_key = "mininotes-secret-key"

# Dossier où l'on va stocker les avatars uploadés par les utilisateurs.
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------------------------------------------------------------------
# Petites fonctions utilitaires
# ---------------------------------------------------------------------------

def current_user():
    """
    Renvoie l'utilisateur actuellement connecté, ou None si personne
    n'est connecté.

    On regarde dans la session (un cookie géré par Flask) s'il y a
    un "user_id". Si oui, on va chercher l'utilisateur correspondant
    dans la base.
    """
    user_id = session.get("user_id")
    if user_id is None:
        return None
    conn = db.get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return user


def login_required(view):
    """
    Petit "décorateur" qui force l'utilisateur à être connecté
    pour accéder à une route. S'il ne l'est pas, on le renvoie
    vers la page de connexion.

    (Un décorateur est une fonction qui enveloppe une autre fonction
    pour ajouter un comportement avant ou après.)
    """
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Inscription
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Page d'inscription.

    - Si la méthode est GET, on affiche le formulaire.
    - Si la méthode est POST, on récupère les champs envoyés
      et on crée un nouvel utilisateur dans la base.
    """
    # Si quelqu'un est déjà connecté, on le renvoie à l'accueil
    if current_user() is not None:
        return redirect(url_for("home"))

    error = None

    if request.method == "POST":
        # On récupère les champs du formulaire
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        is_admin = int(request.form.get("is_admin", 0))

        # Vérifications de base
        if not username or not password:
            error = "Nom d'utilisateur et mot de passe obligatoires."
        else:
            conn = db.get_db()
            # Vérifier que le nom n'est pas déjà pris
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing is not None:
                error = "Ce nom d'utilisateur est déjà pris."
            else:
                # Insérer le nouvel utilisateur dans la table "users"
                conn.execute(
                    "INSERT INTO users (username, password, is_admin) "
                    "VALUES (?, ?, ?)",
                    (username, db.hash_password(password), is_admin),
                )
                conn.commit()
                conn.close()
                # Rediriger vers la page de connexion
                return redirect(url_for("login"))
            conn.close()

    # Afficher la page register.html
    return render_template("register.html", error=error)


# ---------------------------------------------------------------------------
# Connexion et déconnexion
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Page de connexion.

    Après une connexion réussie, on peut rediriger vers une page
    donnée par le paramètre "next" de l'URL (par exemple
    /login?next=/note/3 renverra vers la note 3 après connexion).
    """
    error = None
    next_url = request.args.get("next", "")

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        next_url = request.form.get("next", "")

        # On calcule l'empreinte du mot de passe fourni,
        # et on cherche un utilisateur correspondant dans la base.
        hashed = db.hash_password(password)
        query = (
            "SELECT * FROM users WHERE username = '"
            + username
            + "' AND password = '"
            + hashed
            + "'"
        )
        conn = db.get_db()
        user = conn.execute(query).fetchone()
        conn.close()

        if user is None:
            error = "Nom d'utilisateur ou mot de passe invalide."
        else:
            # On garde l'identifiant de l'utilisateur dans la session.
            # La session est un cookie signé géré par Flask.
            session["user_id"] = user["id"]
            # Rediriger vers la page demandée, ou l'accueil par défaut
            if next_url:
                return redirect(next_url)
            return redirect(url_for("home"))

    return render_template("login.html", error=error, next_url=next_url)


@app.route("/logout")
def logout():
    """Déconnecte l'utilisateur en vidant la session."""
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Page d'accueil : liste des notes de l'utilisateur
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def home():
    """
    Page d'accueil. Affiche les notes appartenant à l'utilisateur
    actuellement connecté, de la plus récente à la plus ancienne.
    """
    user = current_user()
    conn = db.get_db()
    notes = conn.execute(
        "SELECT * FROM notes WHERE owner_id = ? ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    conn.close()
    return render_template("home.html", user=user, notes=notes)


# ---------------------------------------------------------------------------
# Création, lecture, modification, suppression d'une note (CRUD)
# ---------------------------------------------------------------------------

@app.route("/note/new", methods=["GET", "POST"])
@login_required
def note_new():
    """Page de création d'une nouvelle note."""
    user = current_user()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "")

        if not title:
            return render_template(
                "new_note.html", error="Le titre est obligatoire."
            )

        conn = db.get_db()
        conn.execute(
            "INSERT INTO notes (owner_id, title, content) VALUES (?, ?, ?)",
            (user["id"], title, content),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    return render_template("new_note.html")


@app.route("/note/<int:note_id>")
@login_required
def note_view(note_id):
    """Affiche une note existante."""
    conn = db.get_db()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    conn.close()

    if note is None:
        abort(404)

    return render_template("note.html", note=note)


@app.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def note_edit(note_id):
    """Modifie une note existante."""
    conn = db.get_db()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?", (note_id,)
    ).fetchone()

    if note is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "")

        conn.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ?",
            (title, content, note_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("note_view", note_id=note_id))

    conn.close()
    return render_template("note_edit.html", note=note)


@app.route("/note/<int:note_id>/delete", methods=["POST"])
@login_required
def note_delete(note_id):
    """Supprime une note."""
    conn = db.get_db()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/note/<int:note_id>/export")
@login_required
def note_export(note_id):
    """
    Télécharge une note sous forme de fichier texte (.txt).
    """
    conn = db.get_db()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    conn.close()

    if note is None:
        abort(404)

    # On construit le contenu du fichier à partir du titre et du texte
    body = "Titre : " + note["title"] + "\n\n" + note["content"]

    # On renvoie la réponse en indiquant au navigateur que c'est un
    # fichier à télécharger, avec le bon nom.
    response = make_response(body)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=note_" + str(note_id) + ".txt"
    )
    return response


# ---------------------------------------------------------------------------
# Recherche
# ---------------------------------------------------------------------------

@app.route("/search")
@login_required
def search():
    """
    Recherche dans les notes de l'utilisateur connecté.
    Le terme recherché est passé dans l'URL avec ?q=...
    """
    user = current_user()
    q = request.args.get("q", "")

    results = []
    if q:
        conn = db.get_db()
        # On cherche les notes dont le titre ou le contenu contient
        # le terme recherché (LIKE avec des % autour)
        results = conn.execute(
            "SELECT * FROM notes WHERE owner_id = ? "
            "AND (title LIKE ? OR content LIKE ?)",
            (user["id"], "%" + q + "%", "%" + q + "%"),
        ).fetchall()
        conn.close()

    return render_template("search.html", q=q, results=results)


# ---------------------------------------------------------------------------
# Profil utilisateur et upload d'avatar
# ---------------------------------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    Page de profil. Permet d'uploader un avatar (image de profil).
    """
    user = current_user()
    message = None

    if request.method == "POST":
        # request.files contient les fichiers envoyés par le formulaire
        file = request.files.get("avatar")
        if file and file.filename:
            # On enregistre le fichier dans le dossier uploads/
            filename = file.filename
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            # On met à jour la colonne "avatar" de l'utilisateur
            conn = db.get_db()
            conn.execute(
                "UPDATE users SET avatar = ? WHERE id = ?",
                (filename, user["id"]),
            )
            conn.commit()
            conn.close()

            message = "Avatar mis à jour."
            user = current_user()

    return render_template("profile.html", user=user, message=message)


@app.route("/uploads/<path:filename>")
def uploads(filename):
    """
    Sert un fichier depuis le dossier uploads/ (par exemple les
    avatars affichés sur la page de profil).
    """
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_file(path)


# ---------------------------------------------------------------------------
# Page d'administration
# ---------------------------------------------------------------------------

@app.route("/admin")
@login_required
def admin():
    """
    Page d'administration : liste de tous les utilisateurs du site.
    """
    conn = db.get_db()
    users = conn.execute("SELECT id, username, is_admin FROM users").fetchall()
    conn.close()
    return render_template("admin.html", users=users)


# ---------------------------------------------------------------------------
# Lancement de l'application
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Initialise la base de données au démarrage (crée les tables
    # si elles n'existent pas encore).
    db.init_db()
    # Démarre le serveur web de Flask.
    # host="0.0.0.0" permet d'accéder à l'app depuis un autre ordinateur
    # (ou depuis Docker).
    app.run(host="0.0.0.0", port=5000)
