'''Aqui fizemos a instalação da biblioteca pymysql e integração do MySQL'''
'''Foi criado a conexão com o banco local flask_app.'''
'''Criamos a tabela users se não existir com o campo id, cpf, user name, password e account.'''
'''E depois fecha a conexão após a criação da tabela.'''

import pymysql
import pymysql.cursors
class DatabaseModules:
    def __init__(self):
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cpf VARCHAR(20) NOT NULL UNIQUE,
                    user_name VARCHAR(100) NOT NULL,
                    user_password TEXT NOT NULL,
                    account VARCHAR(20) NOT NULL UNIQUE,
                    balance FLOAT
                )
            ''')
        self.conn.commit()
        self.conn.close()

    def get_db_connection(self):
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='My$QLr00t@2025!',
            database='flask_app',
            port=3306,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn