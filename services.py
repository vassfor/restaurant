from datetime import datetime, timedelta

from models import Reservation, Table


class ValidationError(ValueError):
    pass


class TableService:
    def __init__(self, repository, store):
        self.repository = repository
        self.store = store

    def list_tables(self):
        return self.repository.list_all()

    def add(self, name, capacity):
        name = name.strip().upper()
        if not name:
            raise ValidationError("Το Όνομα Τραπεζιού δεν μπορεί να είναι κενό")
        if not capacity.isdigit() or int(capacity) <= 0:
            raise ValidationError("Η χωρητικότητα πρέπει να είναι θετικός αριθμός")
        existing = {table.name.upper() for table in self.repository.list_all()}
        if name in existing:
            raise ValidationError("Το Όνομα Τραπεζιού υπάρχει ήδη")
        self.repository.add(Table(name, int(capacity)))
        self._sync_store()

    def delete(self, name):
        name = name.strip().upper()
        if not name:
            raise ValidationError("Επιλέξτε διαθέσιμο τραπέζι")
        if not any(table.name.upper() == name for table in self.repository.list_all()):
            raise ValidationError("Επιλέξτε διαθέσιμο τραπέζι")
        self.repository.delete(name)
        self._sync_store()

    def _sync_store(self):
        self.store.save(self.store.business_name(), self.repository.list_all())


class ReservationService:
    def __init__(self, repository, table_repository):
        self.repository = repository
        self.table_repository = table_repository

    def validate(self, name, phone, target_date, target_time, people, table_name, now=None):
        name = name.strip()
        phone = phone.strip()
        table_name = table_name.strip().upper()
        if not name:
            raise ValidationError("Το Όνομα Πελάτη δεν μπορεί να είναι κενό")
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise ValidationError("Το Τηλέφωνο Πελάτη πρέπει να αποτελείται από 10 ψηφία")
        if not people.isdigit() or int(people) <= 0:
            raise ValidationError("Ο Αριθμός Ατόμων πρέπει να είναι θετικός αριθμός")
        now = now or datetime.now()
        if target_date < now.date():
            raise ValidationError(f"Η Ημερομηνία Κράτησης δεν μπορεί να είναι πριν τη σημερινή {now.date()}")
        if target_date == now.date() and target_time < now.time().replace(second=0, microsecond=0):
            raise ValidationError(
                f"Η Ώρα Κράτησης για την τρέχουσα ημερομηνία δεν μπορεί να είναι πριν την τρέχουσα ώρα {now.time().replace(second=0, microsecond=0)}"
            )
        tables = self.table_repository.list_all()
        if not any(table.name.upper() == table_name for table in tables):
            raise ValidationError("Επιλέξτε διαθέσιμο τραπέζι")
        return name, phone, int(people), table_name

    def create(self, name, phone, target_date, target_time, people, table_name):
        name, phone, people, table_name = self.validate(
            name, phone, target_date, target_time, people, table_name
        )
        reservation = Reservation(0, table_name, name, phone, target_date, target_time, people)
        return self.repository.add(reservation)

    def update(self, reservation_id, name, phone, target_date, target_time, people, table_name):
        name, phone, people, table_name = self.validate(
            name, phone, target_date, target_time, people, table_name
        )
        reservation = Reservation(reservation_id, table_name, name, phone, target_date, target_time, people)
        return self.repository.update(reservation)

    def cancel(self, reservation_id):
        return self.repository.delete(reservation_id)

    def active_reservations(self, now=None):
        now = now or datetime.now()
        target_date = now.date()
        start = (now - timedelta(hours=2)).time().replace(second=0, microsecond=0)
        end = (now + timedelta(hours=2)).time().replace(second=0, microsecond=0)
        self.repository.delete_expired(target_date, start)
        return self.repository.active_window(target_date, start, end)
