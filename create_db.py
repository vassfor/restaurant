import mysql.connector

def create_db(host, usr, pwd, db_name):
    connection = mysql.connector.connect(
        host = host,
        user = usr,
        password = pwd
    )
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        print(f"Database '{db_name}' created or already exists")
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()