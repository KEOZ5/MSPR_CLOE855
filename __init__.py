from flask import Flask, render_template, request, abort
import sqlite3
from functools import wraps

app = Flask(__name__)

# Fonction pour se connecter à la base de données SQLite
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour vérifier l'authentification de l'utilisateur
def check_auth(username, password):
    return username == 'user' and password == '12345'

# Fonction pour exiger une authentification
def authenticate():
    return abort(401, description="Authentification requise")

# Route d'accueil
@app.route('/')
def hello_world():
    return "Hello World!"

# Route pour afficher un client en fonction de son ID
@app.route('/fiche_client/<int:id>', methods=['GET'])
def fiche_client(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (id,))
    client = cursor.fetchone()
    if client:
        return render_template('fiche_client.html', client=client)
    else:
        return f"Aucun client trouvé avec l'ID {id}.", 404

# Route pour afficher tous les clients
@app.route('/consultation/', methods=['GET'])
def consultation():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    return render_template('consultation.html', clients=clients)

# Route pour enregistrer un nouveau client
@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    if request.method == 'POST':
        # On récupère les données du formulaire
        nom = request.form['nom']
        email = request.form['email']
        # Insertion dans la base de données
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (nom, email) VALUES (?, ?)", (nom, email))
        conn.commit()
        return f"Client {nom} ajouté avec succès!"
    return render_template('enregistrer_client.html')

# Route pour la page de connexion (authentification)
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_auth(username, password):
            return f"Bienvenue, {username}!"
        else:
            return "Authentification échouée, essayez à nouveau", 401
    return render_template('login.html')

# Route pour afficher un client par nom
@app.route('/fiche_nom/<string:nom>', methods=['GET'])
def fiche_nom(nom):
    # Vérification de l'authentification de l'utilisateur
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    # Connexion à la base de données
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom,))
    client = cursor.fetchone()

    if client:
        return render_template('fiche_client.html', client=client)
    else:
        return f"Aucun client trouvé avec le nom {nom}.", 404

# Fonction pour initialiser la base de données
@app.cli.command('initdb')
def initdb():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nom TEXT NOT NULL,
                      email TEXT NOT NULL)''')
    conn.commit()
    print("Base de données initialisée!")

if __name__ == '__main__':
    app.run(debug=True)
