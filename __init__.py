from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

# Fonction pour enregistrer la connexion dans la base de données
def log_connexion(username, ip_address):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(''' 
    INSERT INTO logs_connexions (username, ip_address) VALUES (?, ?)
    ''', (username, ip_address))
    conn.commit()
    conn.close()

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))
    
    # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vérifier les identifiants
        if username == 'admin' and password == 'password':  # password à cacher par la suite
            session['authentifie'] = True
            # Loguer la connexion
            log_connexion(username, request.remote_addr)
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement

# Nouvelle route pour rechercher un client par son nom
@app.route('/fiche_nom/<string:nom>', methods=['GET'])
def fiche_nom(nom):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Recherche du client par nom dans la base de données (utilisation de LIKE pour recherche partielle)
    cursor.execute("SELECT * FROM clients WHERE nom LIKE ?", ('%' + nom + '%',))
    client = cursor.fetchall()
    conn.close()

    if client:
        return render_template('read_data.html', data=client)  # Afficher les résultats dans le template
    else:
        return f"Aucun client trouvé avec le nom {nom}.", 404  # Si aucun client n'est trouvé

if __name__ == "__main__":
    app.run(debug=True)
