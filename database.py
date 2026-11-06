import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, settings):
        self.settings = settings

    def connect(self, include_database=True):
        params = {
            "host": self.settings.host,
            "user": self.settings.user,
            "password": self.settings.password,
        }
        if include_database:
            params["database"] = self.settings.database
        return mysql.connector.connect(**params)

    def initialize(self):
        connection = self.connect(include_database=False)
        try:
            cursor = connection.cursor()
            database = self.settings.database.replace("`", "``")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
            connection.commit()
        finally:
            cursor.close()
            connection.close()

        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Tables(
                    name VARCHAR(10) PRIMARY KEY,
                    capacity INT NOT NULL
                )
                """
            )
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
                )
                """
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()


def rollback_safely(connection):
    try:
        connection.rollback()
    except Error:
        pass
