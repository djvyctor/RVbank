import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import random
from  flask_session import Session
from database import *
from auxiliarys import *



class RoutesWeb:
    def __init__(self):
        #inicializa o banco de dados
        self.data = DatabaseModules()
        
        #incializa as funções axuliares(por equanto apenas a geração de contas)
        self.auxiliary =  AuxiliaryFunctions()
        
        #inicialização da aplicação web
        self.app = Flask(__name__)

        #chave secreta para cookies e sessões
        self.app.secret_key = 'nothing_here'

        #Iniclização de Socketio(ainda sem utilização, mas será usado para ataulização do saldo)
        self.socketio =SocketIO(self.app, 
                                cors_allowed_origins='*', #apenas em fase de testes
                                 manage_session=True) #usaraá as mesmas sessões do flask


        # aguardar os usuarios conectados
        self.connected_users = set()

        #persistencia de dados (fylesystem)
        self.app.config['SESSION_TYPE'] = 'filesystem'
        
        #incialização do contro de sessões
        Session(self.app)

    def main(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True)

    
    def login_sets(self,type_of_method):

        #obtem os dados do html por nome da tag e armazena em variavel
        if type_of_method == "POST":
            # name = request.form['name']
            cpf = request.form['cpf']
            password = request.form['password']

            #abre uma conexão com o banco de dados
            conn = self.data.get_db_connection()
            
            #executa uma consulta ao SQL para buscar o usuario pelo CPF
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE cpf = %s", (cpf, ))
                user = cursor.fetchone()
                
            #verifica se o usuario existe e se a senha bate com o hash
            if user and check_password_hash(user['user_password'], password):
                #armazenamento de dados que serão usados na sessão
                session['user_id'] = user['id']
                session['user_name'] = user['user_name']
                session['user_cpf'] = user['cpf']
                session['user_account'] = user['account']
                session['user_balance'] = user ['balance']

                #redirecionamento ao "menu geral" da aplicação
                return redirect(url_for("main"))
            
            flash("usuario nao existente ou senha incorreta")#pra exibição no html caso não exista um usuario com essas credenciais
            
        #se nenhum metodo acima rendereizou outra pagina, essa aqui será renderizada
        return render_template("login.html")

    def register_sets(self, type_of_method):
        #verifica se o metodo é post
        if type_of_method == "POST":
            #armazena os dados do html por nome em uma variavel
            name = request.form['name']
            cpf = request.form['cpf']
            password = request.form['password']

            initial_balance = 0.00 #o usuario sera cadastrado com 0 no saldo

            #hash para senhas (segurança)
            hash_password = generate_password_hash(password)

            #abre a conexão com o mysql
            conn = self.data.get_db_connection()

            try:
                #roda até encontrar uma conta não atribuida a outro usuario
                while True: 
                    #gera a variavel account com um valor aleatorio com a mascara (0000-0)
                    account = self.auxiliary.generate_account_number()
                    with conn.cursor() as cursor:
                        #executa a busca no banco de dados
                        cursor.execute("SELECT 1 FROM users WHERE account = %s", (account,))
                        #armazena o dado no exists
                        exists = cursor.fetchone()

                    if exists: #se exists tiver algum valor continua a repetição while
                        continue

                    try:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO users (user_name, cpf, user_password, account, balance) VALUES (%s, %s, %s, %s, %s)",
                                (name, cpf, hash_password, account, initial_balance)
                            )#armazena os dados preenchidos em register.html no banco de dados
                        conn.commit() #salva os dados no banco de dados
                        
                        flash("Registrado com sucesso")#gera uma mensagem no html caso seja armazenado com sucesso
                        #redireciona ao login caso sucesso
                        return redirect(url_for("login"))

                    except pymysql.err.IntegrityError as e:#se houver um erro atribui ao "e"
                        print("Erro de integridade:", e)
                        flash("Já existe um usuário com essas credenciais")#mensagem ao html
                        return render_template("register.html")#mantem na pagina para tentar um novo cadastro

            finally:
                conn.close()#desconexão com o banco de dados. crucial para a segurança e integridade

        return render_template("register.html")#caso algo não deu certo, retorna ao banco

    def main_sets(self):
        #verifica se o usuario esta logado na sessão do flask
        if 'user_id' not in session and 'user_cpf' not in session:
            flash("sem sessao")
            return redirect(url_for('login'))# se são logado, retorna a pagina de login
    
        return render_template("main.html", name=session['user_name'],account=session['user_account'], balance=str(session['user_balance']).replace(".",","))#renderiza e retorna os dados do usuario à pagina main.html 
