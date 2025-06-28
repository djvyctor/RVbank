from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
from  flask_session import Session
from database import *



class RoutesWeb:
    def __init__(self):
        self.local_database = DatabaseModules()
        self.data = DatabaseModules()
        self.app = Flask(__name__)
        self.app.secret_key = 'nothing_here'
        self.socketio =SocketIO(self.app, cors_allowed_origins='*', manage_session=True)
        
        self.connected_users = set()
        self.app.config['SESSION_TYPE'] = 'filesystem'
        Session(self.app)

    def main(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True)

    
    def login_sets(self,type_of_method):
        if type_of_method == "POST":
            name = request.form['name']
            cpf = request.form['cpf']
            password = request.form['password']
            conn = self.data.get_db_connection()

            user = conn.execute("SELECT * FROM users WHERE cpf = ?", (cpf, )).fetchone()

            if user and check_password_hash(user['user_password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['user_name']
                session['user_cpf'] = user['cpf']
                session['user_account'] = user['account']
                session['user_balance'] = user ['balance']

                return redirect(url_for("main"))
            flash("usuario existente")
        return render_template("login.html")