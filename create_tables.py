import mysql.connector

def create_tables(host, usr, pwd, db_name):
    connection = mysql.connector.connect(
        host = host,
        user = usr,
        password = pwd,
        database = db_name
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Tables(
                name VARCHAR(10) PRIMARY KEY,
                capacity INT NOT NULL
            );
            """
        )
        connection.commit()
        print("Table 'Tables' succesfully created")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Reservations(
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(10) NOT NULL,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(10),
                date DATE NOT NULL,
                time TIME NOT NULL,
                people INT NOT NULL,
                FOREIGN KEY(table_name) REFERENCES Tables(name)
            );
            """
        )
        connection.commit()
        print("Table 'Reservations' succesfully created")
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()