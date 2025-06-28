"""RICHARD!!!

ESTE É UM CÓDIGO IGUAL O SEU MAS PENSANDO NA SEGURANÇA. 
é como se fosse o (app.py)
DE UMA OLHADA DEPOIS E ME FALA!!!"""

import os
import re
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # CHAVE DINÂMICA
app.config['SESSION_PERMANENT'] = False

# --- FUNÇÕES AUXILIARES ---
def validar_cpf(cpf):
    """Valida formato e dígitos verificadores de CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0]*11: 
        return False
    
    # Cálculo dígito verificador
    for i in range(9, 11):
        valor = sum(int(cpf[num]) * (i+1 - num) for num in range(0, i))
        digito = (valor * 10) % 11
        if digito == 10: digito = 0
        if digito != int(cpf[i]): 
            return False
    return True

def get_db_connection():
    conn = sqlite3.connect('./data/database.db', timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# --- ROTAS PRINCIPAIS ---
@app.route("/", methods=['GET','POST'])
def login():
    if request.method == "POST":
        cpf = re.sub(r'[^0-9]', '', request.form['cpf'])
        password = request.form['password']
        
        if not validar_cpf(cpf):
            flash('CPF inválido', 'danger')
            return render_template("login.html")
        
        conn = get_db_connection()
        try:
            user = conn.execute(
                'SELECT id, nome, senha_hash FROM users WHERE cpf = ?', 
                (cpf,)
            ).fetchone()
            
            if user and check_password_hash(user['senha_hash'], password):
                session.clear()
                session['user_id'] = user['id']  # CRIA SESSÃO SEGURA
                session['user_nome'] = user['nome']
                return redirect(url_for('dashboard'))
        finally:
            conn.close()
        
        flash('Credenciais inválidas', 'danger')  # MENSAGEM GENÉRICA
    
    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nome = request.form['name'].strip()
        cpf = re.sub(r'[^0-9]', '', request.form['cpf'])
        senha = request.form['password']
        
        # VALIDAÇÕES
        erros = []
        if len(nome) < 3: erros.append('Nome muito curto')
        if not validar_cpf(cpf): erros.append('CPF inválido')
        if len(senha) < 8: erros.append('Senha precisa ter 8+ caracteres')
        
        if erros:
            for erro in erros: flash(erro, 'danger')
            return render_template("register.html")
        
        conn = get_db_connection()
        try:
            hash_senha = generate_password_hash(senha)
            conn.execute(
                "INSERT INTO users (nome, cpf, senha_hash) VALUES (?,?,?)",
                (nome, cpf, hash_senha)
            )
            conn.commit()
            flash('Registro realizado! Faça login', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('CPF já cadastrado', 'danger')
        finally:
            conn.close()
        
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return f"Bem-vindo, {session['user_nome']}!"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL
            )''')
        conn.commit()
    
    app.run(host='0.0.0.0', port=5000, debug=False)  # DEBUG DESLIGADO EM PROD!