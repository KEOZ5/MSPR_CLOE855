from flask import Flask, render_template, request, Response, redirect, url_for
import sqlite3

app = Flask(__name__)

# Fonction pour vérifier l'authentification
def check_auth(username, password):
    return username == 'user' and password == '12345'

# Fonction pour demander l'authentification si elle échoue
def authenticate():
    return Response(
        'Authentification requise', 401,
        {'WWW-Authenticate': 'Basic realm="Login required"'})

# Connexion à la base de données SQLite
def get_db():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/')
def home():
    return render_template('helloWorld.html')

@app.route('/lecture')
def lecture():
    return "Lecture des données - accès conditionné"

@app.route('/authentification')
def authentification():
    return "Page d'authentification (Login: admin, Mot de passe: password)"

@app.route('/fiche_client/<int:id>')
def fiche_client(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (id,))
    client = cursor.fetchone()
    if client:
        return render_template('fiche_client.html', client=client)
    else:
        return f"Aucun client trouvé avec l'ID {id}.", 404

@app.route('/consultation/')
def consultation():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    return render_template('consultation.html', clients=clients)

# Route protégée par authentification
@app.route('/fiche_nom/<string:nom>', methods=['GET'])
def fiche_nom(nom):
    # Vérification de l'authentification avant de continuer
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    # Récupération des informations du client par nom
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom,))
    client = cursor.fetchone()

    if client:
        return render_template('fiche_client.html', client=client)
    else:
        return f"Aucun client trouvé avec le nom {nom}.", 404

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (nom, email) VALUES (?, ?)", (nom, email))
        conn.commit()
        return redirect(url_for('consultation'))

if __name__ == "__main__":
    app.run(debug=True)
