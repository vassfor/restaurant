import tkinter as tk
from tkinter import messagebox

from models import Table


class SetupWizard:
    def __init__(self, root, table_service, store):
        self.root = root
        self.table_service = table_service
        self.store = store
        self.entries = []

    def run(self):
        self.root.title("Setup page")
        self.root.geometry("800x600")
        self.root.configure(bg="#17202A")
        self._welcome()

    def _welcome(self):
        self._clear()
        tk.Label(
            self.root,
            text="Καλωσήρθατε!",
            font=("Arial", 25),
            bg="#17202A",
            fg="#EAECEE",
        ).place(relx=0.5, rely=0.2, anchor="center")
        button = self._button("Έναρξη", self._business_details)
        button.place(relx=0.5, rely=0.5, anchor="center")

    def _business_details(self):
        self._clear()
        tk.Label(
            self.root,
            text="Όνομα Επιχείρησης:",
            font=("Arial", 15),
            bg="#17202A",
            fg="#EAECEE",
        ).place(relx=0.5, rely=0.35, anchor="center")
        self.business_entry = tk.Entry(self.root, font=("Arial", 15), bg="#2C3E50", fg="#EAECEE")
        self.business_entry.place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(
            self.root,
            text="Αριθμός Τραπεζιών:",
            font=("Arial", 15),
            bg="#17202A",
            fg="#EAECEE",
        ).place(relx=0.5, rely=0.55, anchor="center")
        self.count_entry = tk.Entry(self.root, font=("Arial", 15), bg="#2C3E50", fg="#EAECEE")
        self.count_entry.place(relx=0.5, rely=0.6, anchor="center")
        button = self._button("Επόμενο", self._table_details)
        button.place(relx=0.5, rely=0.8, anchor="center")

    def _table_details(self):
        business_name = self.business_entry.get().strip()
        count = self.count_entry.get().strip()
        if not business_name:
            messagebox.showerror("Error", "Το Όνομα Επιχείρησης δεν μπορεί να είναι κενό")
            return
        if not count.isdigit() or int(count) <= 0:
            messagebox.showerror("Error", "Ο Αριθμός Τραπεζιών πρέπει να είναι θετικός αριθμός")
            return
        self._clear()
        tk.Label(
            self.root,
            text="Παρακαλώ εισάγετε το όνομα κάθε τραπεζιού και τη χωρητικότητά του σε άτομα",
            font=("Arial", 13),
            bg="#17202A",
            fg="#EAECEE",
        ).pack(pady=10)
        frame = tk.Frame(self.root, bg="#17202A")
        frame.pack(pady=10)
        tk.Label(frame, text="Όνομα τραπεζιού", font=("Arial", 13), bg="#17202A", fg="#EAECEE").grid(row=0, column=0, padx=10, pady=8)
        tk.Label(frame, text="Χωρητικότητα", font=("Arial", 13), bg="#17202A", fg="#EAECEE").grid(row=0, column=1, padx=10, pady=8)
        self.entries = []
        for index in range(int(count)):
            name = tk.Entry(frame, font=("Arial", 13), bg="#2C3E50", fg="#EAECEE", width=10)
            capacity = tk.Entry(frame, font=("Arial", 13), bg="#2C3E50", fg="#EAECEE", width=10)
            name.grid(row=index + 1, column=0, padx=10, pady=8)
            capacity.grid(row=index + 1, column=1, padx=10, pady=8)
            self.entries.append((name, capacity))
        self.business_name = business_name
        self._button("Ολοκλήρωση", self._save).pack(pady=10)

    def _save(self):
        tables = []
        seen = set()
        try:
            for name_entry, capacity_entry in self.entries:
                name = name_entry.get().strip().upper()
                capacity = capacity_entry.get().strip()
                if not name:
                    raise ValueError("Το Όνομα Τραπεζιού δεν μπορεί να είναι κενό")
                if not capacity.isdigit() or int(capacity) <= 0:
                    raise ValueError("Η χωρητικότητα πρέπει να είναι θετικός αριθμός")
                if name in seen:
                    raise ValueError(f"Το Όνομα Τραπεζιού '{name}' υπάρχει ήδη")
                seen.add(name)
                tables.append(Table(name, int(capacity)))
            self.store.save(self.business_name, tables)
            self.table_service.repository.replace_all(tables)
            messagebox.showinfo("Success", "Τα δεδομένα της επιχείρησής σας εισήχθησαν με επιτυχία!")
            self.root.destroy()
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {exc}")

    def _clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    @staticmethod
    def _button(self, text, command):
        button = tk.Button(self.root,
            text=text,
            font=("Arial", 15),
            bg="#2C3E50",
            fg="#EAECEE",
            command=command,
        )
        button.bind("<Enter>", lambda event: event.widget.config(bg="#FF5733"))
        button.bind("<Leave>", lambda event: event.widget.config(bg="#2C3E50"))
        return button
