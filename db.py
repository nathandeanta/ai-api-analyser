import sqlite3


def init_db():
    conn = sqlite3.connect('identifier.db')
    cursor = conn.cursor()

    # Criação da tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
           CREATE TABLE IF NOT EXISTS theft(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               type TEXT  NOT NULL,
               desc TEXT NOT NULL
           )
       ''')
    conn.commit()
    conn.close()

def conect_database():
    return sqlite3.connect('identifier.db')