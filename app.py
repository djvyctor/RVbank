from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from  flask_session import Session



app = Flask(__name__)
app.secret_key='12345678'
socketio=SocketIO(app, cors_allowed_origins='*', manage_session=True)



@app.route("/")
def login():
    return render_template("login.html")



if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
