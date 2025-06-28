from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
from  flask_session import Session

app = Flask(__name__)
app.secret_key='nothing_here'
socketio=SocketIO(app, cors_allowed_origins='*', manage_session=True)


users_conecteds=set()
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def get_db_connection():
    conn = sqlite3.connect('./data/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_account_number():
    """
    gera um numero de conta randomizado.
    """
    number =  random.randint(0,9999)
    checker = random.randint(0,9)

    return f"{number:04d}-{checker}"


@app.route("/",methods=['GET','POST'])
def login():
    if request.method=="POST":
        name = request.form["name"]
        cpf = request.form['cpf']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE cpf = ?', (cpf,)).fetchone()    

        if user and check_password_hash(user['senha_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['nome']
            session['user_cpf'] = user['cpf']
            session['user_account'] = user['conta']
            session['user_balance'] = user['saldo']

            return redirect(url_for("main"))
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
        initial_balance = 0.00
        hash_password = generate_password_hash(password)
        conn = get_db_connection() #abrir o uso do banco


        while True:
            account = generate_account_number()
            exists = conn.execute("SELECT 1 FROM users WHERE conta = ?", (account, )).fetchone()
            if not exists:
                break
        try:
            conn.execute("INSERT INTO users (nome,cpf,senha_hash, conta, saldo) VALUES (?,?,?,?,?)", (name,cpf,hash_password,account,initial_balance))
            conn.commit()
            flash("registrado")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Já existe um usuario com esse CPF")
        finally:
            conn.close()  #segurança do banco de dados, fechar o banco apos o uso.
        
    return render_template("register.html")

@app.route("/main")
def main():
    if 'user_id' not in session and 'user_cpf' not in session:
        return redirect(url_for('login'))
    
    return render_template("main.html", name=session['user_name'],account=session['user_account'], balance=str(session['user_balance']).replace(".",","))

if __name__ == "__main__":
    conn = get_db_connection()
    
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                conta TEXT NOT NULL UNIQUE,
                saldo REAL)

        ''')

    conn.commit()
    conn.close()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)