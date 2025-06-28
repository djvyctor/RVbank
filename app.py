from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from  flask_session import Session



app = Flask(__name__)
app.secret_key='nothing_here'
socketio=SocketIO(app, cors_allowed_origins='*', manage_session=True)


def get_db_connection():
    conn = sqlite3.connect('./data/database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/",methods=['GET','POST'])
def login():
    if request.method=="POST":
        name = request.form["name"]
        cpf = request.form['cpf']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * from users WHERE nome = ?', (name, )).fetchone()     

        if user and check_password_hash(user['senha_hash'], password):
            print("funcionou")
            flash("usuario existe")
        flash("usuario nao existe")
    
    return render_template("login.html")
    
@app.route("/register", methods=['GET','POST'])
def register():
    """
    1-cadastro de usuario no banco de dados
    param:
        name: nome de usuario (obrigatorio)
        cpf: unicos(obrigatorio)
        senha: (obrigatorio) 
    """
    if request.method == 'POST':
        name = request.form['name']
        cpf = request.form['cpf']
        password = request.form['password']
        hash_password = generate_password_hash(password)
        conn = get_db_connection()

        try:
            conn.execute("INSERT INTO users (nome,cpf,senha_hash) VALUES (?,?,?)", (name,cpf,hash_password))
            conn.commit()
            flash("registrado")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Já existe um usuario com esse CPF")
        finally:
            conn.close()
        
    return render_template("register.html")

if __name__ == "__main__":
    conn = get_db_connection()
    
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL)
        ''')

    conn.commit()
    conn.close()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)