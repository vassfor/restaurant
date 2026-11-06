from models import Reservation, Table


class TableRepository:
    def __init__(self, database):
        self.database = database

    def list_all(self):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name, capacity FROM Tables ORDER BY name")
            return [Table(name, capacity) for name, capacity in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def count(self):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Tables")
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            connection.close()

    def add(self, table):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Tables(name, capacity) VALUES(%s, %s)",
                (table.name, table.capacity),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def delete(self, name):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Tables WHERE name = %s", (name,))
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def replace_all(self, tables):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.executemany(
                "INSERT INTO Tables(name, capacity) VALUES(%s, %s)",
                [(table.name, table.capacity) for table in tables],
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()


class ReservationRepository:
    def __init__(self, database):
        self.database = database

    def add(self, reservation):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO Reservations(table_name, name, phone, date, time, people)
                VALUES(%s, %s, %s, %s, %s, %s)
                """,
                (
                    reservation.table_name,
                    reservation.name,
                    reservation.phone,
                    reservation.date,
                    reservation.time,
                    reservation.people,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, reservation):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE Reservations
                SET table_name=%s, name=%s, phone=%s, date=%s, time=%s, people=%s
                WHERE id=%s
                """,
                (
                    reservation.table_name,
                    reservation.name,
                    reservation.phone,
                    reservation.date,
                    reservation.time,
                    reservation.people,
                    reservation.id,
                ),
            )
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def delete(self, reservation_id):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Reservations WHERE id = %s", (reservation_id,))
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def list_for_date(self, target_date):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, table_name, name, COALESCE(phone, ''), date, time, people
                FROM Reservations
                WHERE date=%s
                ORDER BY time, table_name
                """,
                (target_date,),
            )
            return [Reservation(*row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def active_window(self, target_date, start_time, end_time):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, table_name, name, COALESCE(phone, ''), date, time, people
                FROM Reservations
                WHERE date=%s AND time BETWEEN %s AND %s
                ORDER BY time
                """,
                (target_date, start_time, end_time),
            )
            return [Reservation(*row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def delete_expired(self, target_date, cutoff_time):
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE FROM Reservations
                WHERE date < %s OR (date = %s AND time <= %s)
                """,
                (target_date, target_date, cutoff_time),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
