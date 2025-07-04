from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_socketio import SocketIO, emit, join_room
from app.database import DatabaseModules
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import generate_account_number

impoted_module = DatabaseModules()

def setup_routes(app):
    @app.route("/login",methods=["GET",'POST'])
    def login():
        if request.method == "POST":
            cpf = request.form['cpf']
            password = request.form['password']
            conn = DatabaseModules()
            conn = conn.get_db_connection()
            
            with conn.cursor() as cursor: #passar para o utils depois
                cursor.execute("SELECT * FROM users WHERE cpf = %s", (cpf,))
                user = cursor.fetchone()
            if user and check_password_hash(user['user_password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['user_name']
                session['user_cpf'] = user['cpf']
                session['user_account'] = user['account']
                session['user_balance'] = user['balance']
                return redirect(url_for("main"))
            flash("Usuário não existe ou senha incorreta")

        return render_template("login.html")
    
    @app.route("/register", methods=['GET', 'POST'])
    def register(): 
        if request.method == "POST":
            name = request.form['name']
            cpf = request.form['cpf']
            password = request.form['password']
            initial_balance = 0.00
            hash_password = generate_password_hash(password)
            conn = DatabaseModules()
            conn = conn.get_db_connection()
            try:
                while True:
                    account_number = generate_account_number()
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT * FROM users WHERE account = %s", (account_number,))
                        if not cursor.fetchone():
                            break

                with conn.cursor() as cursor: #passar para o utils depois 
                    cursor.execute(
                        "INSERT INTO users (user_name, cpf, user_password, account, balance) VALUES (%s, %s, %s, %s, %s)",
                        (name, cpf, hash_password, account_number, initial_balance)
                    )
                conn.commit()
                flash("Usuário cadastrado com sucesso!")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"Erro ao cadastrar usuário: {str(e)}")
                conn.rollback()
            finally:
                conn.close()

        return render_template("register.html")
    
    @app.route("/main")
    def main(): 
        if 'user_id' not in session or 'user_cpf' not in session:
            flash("Você precisa estar logado para acessar esta página.")
            return redirect(url_for('login'))
        conn = DatabaseModules()
      
        user = conn.get_data(session['user_cpf'])
        print(user)
        return render_template("main.html", 
                               name=session['user_name'], 
                               account=session['user_account'], 
                               balance=str(user['balance']).replace(".", ","))

    @app.route("/pix", methods=["GET", "POST"])
    def pix():
        conn = DatabaseModules()
        conn = conn.get_db_connection()
        connection = DatabaseModules()
        current_user =  connection.get_data(session['user_cpf'])
        if request.method == "POST":
            destination_cpf = request.form['pix_key']
            amount = request.form['amount']
            user = connection.get_data(destination_cpf)
            
            current_balance = current_user['balance']
            
            if current_user['balance'] < float(amount):
                flash("Saldo insuficiente para realizar a transação.")
                return redirect(url_for('pix'))
            else:
                current_balance -= float(amount)
                connection.update_data(current_balance, session['user_cpf'])
                if user:
                    current_balance_destiny = user['balance'] + float(amount)
                    connection.update_data(current_balance_destiny, destination_cpf)
                # flash("Transferência realizada com sucesso!")
                return redirect(url_for('main'))

        if 'user_id' not in session or 'user_cpf' not in session:
            flash("Você precisa estar logado para acessar esta página.")
            return redirect(url_for('login'))
        
        

        return render_template("pix.html", 
                               name=session['user_name'], 
                               account=session['user_account'], 
                               balance=str(current_user['balance']).replace(".", ","))
    