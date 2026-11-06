import os
import tkinter as tk

from app import RestaurantApp
from config import Settings
from database import Database
from repositories import ReservationRepository, TableRepository
from services import ReservationService, TableService
from setup_wizard import SetupWizard
from storage import BusinessDataStore


def bootstrap():
    settings = Settings.from_env()
    database = Database(settings)
    database.initialize()

    store = BusinessDataStore()
    table_repository = TableRepository(database)
    reservation_repository = ReservationRepository(database)

    if not store.exists():
        root = tk.Tk()
        SetupWizard(root, TableService(table_repository, store), store).run()
        return

    if table_repository.count() == 0:
        legacy_tables = store.tables()
        if legacy_tables:
            table_repository.replace_all(legacy_tables)

    root = tk.Tk()
    app = RestaurantApp(
        root,
        settings,
        TableService(table_repository, store),
        ReservationService(reservation_repository, table_repository),
        store,
    )
    app.run()


if __name__ == "__main__":
    bootstrap()
