import sqlite3

class DatabaseModules:
    def __init__(self):
        self.conn = self.get_db_connection()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL UNIQUE,
                user_name TEXT NOT NULL,
                user_password TEXT NOT NULL,
                account TEXT NOT NULL UNIQUE,
                balance REAL)

        ''')
        self.conn.commit()
        self.conn.close()

    def get_db_connection(self):
        conn = sqlite3.connect("./data/database.db")
        conn.row_factory = sqlite3.Row
        return conn