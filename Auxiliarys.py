from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import random
from  flask_session import Session

class AuxiliaryFunctions:
    def __init__(self):
      pass
    def generate_account_number(self):
        """generates random numbers for accounts"""
        
        number = random.randint(0,9999)
        checker = random.randint(0,9)

        return f"{number:04d}-{checker}"
    
