import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date, datetime, timedelta

from services import ValidationError


BG = "#17202A"
PANEL = "#64727A"
BUTTON = "#2C3E50"
TEXT = "#EAECEE"
BUSY = "#FF5733"


class RestaurantApp:
    def __init__(self, root, settings, table_service, reservation_service, store):
        self.root = root
        self.settings = settings
        self.table_service = table_service
        self.reservation_service = reservation_service
        self.store = store
        self.tables = []
        self.table_items = {}
        self.status_buttons = {}
        self.manual_busy = set()
        self.table_sizes = {}
        self.root.title("Σύστημα Διαχείρισης Κρατήσεων Εστιατορίου")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG)

    def run(self):
        self._build()
        self.root.after(200, self.draw_tables)
        self.root.after(2000, self.update_status)
        self.root.mainloop()

    def _build(self):
        self.tables = self.table_service.list_tables()
        self.table_sizes = {table.name: table.capacity for table in self.tables}
        tk.Label(
            self.root,
            text=f"{self.store.business_name()}   Reservations",
            font=("Arial", 25, "bold"),
            bg=BG,
            fg=TEXT,
        ).pack(pady=(20, 10))

        self.time_label = tk.Label(self.root, text="", font=("Arial", 15), bg=BG, fg=TEXT)
        self.time_label.place(x=70, y=90)
        self._update_time()

        self.canvas = tk.Canvas(self.root, width=880, height=640, bg=BG)
        self.canvas.pack(pady=(10, 10), padx=(20, 0), side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.bind("<Configure>", lambda event: self.draw_tables())

        add = self._button(self.canvas, "Νέο τραπέζι", self.new_table)
        add.place(relx=0.4, rely=0.95, anchor="c")
        remove = self._button(self.canvas, "Κατάργηση τραπεζιού", self.delete_table)
        remove.place(relx=0.6, rely=0.95, anchor="c")

        panel = tk.Canvas(self.root, width=260, height=640, bg=BG)
        panel.pack(pady=(10, 10), padx=(10, 20), side=tk.RIGHT)
        panel.create_line(0, 470, 700, 470, fill="white", width=3)
        self._build_reservation_form(panel)

    def _build_reservation_form(self, panel):
        self._label(panel, "Όνομα", 0.05)
        self.name_entry = self._entry(panel, 0.10)
        self._label(panel, "Τηλέφωνο", 0.15)
        self.phone_entry = self._entry(panel, 0.20)

        self._label(panel, "Ημέρα     Μήνας    Έτος", 0.25)
        self.day_entry, self.month_entry, self.year_entry = self._date_controls(panel, 0.30)

        self._label(panel, "Ώρα", 0.35)
        self.hour_entry, self.minute_entry = self._time_controls(panel, 0.40)

        self._label(panel, "Άτομα", 0.45)
        self.people_entry = self._entry(panel, 0.50)
        self._label(panel, "Τραπέζι", 0.55)
        self.table_entry = self._entry(panel, 0.60)

        self._button(panel, "Νέα κράτηση", self.create_reservation).place(relx=0.5, rely=0.68, anchor="center")

        self._label(panel, "Ημέρα     Μήνας    Έτος", 0.80)
        self.show_day, self.show_month, self.show_year = self._date_controls(panel, 0.85)
        self._button(panel, "Εμφάνιση κρατήσεων", self.show_reservations).place(relx=0.5, rely=0.95, anchor="center")

    def _date_controls(self, parent, rely):
        days = [f"{i:02}" for i in range(1, 32)]
        months = [f"{i:02}" for i in range(1, 13)]
        years = [str(i) for i in range(date.today().year, date.today().year + 5)]
        day = ttk.Combobox(parent, values=days, state="readonly")
        month = ttk.Combobox(parent, values=months, state="readonly")
        year = ttk.Combobox(parent, values=years, state="readonly")
        day.set(f"{date.today().day:02}")
        month.set(f"{date.today().month:02}")
        year.set(str(date.today().year))
        day.place(relx=0.35, rely=rely, anchor="e", relwidth=0.18)
        month.place(relx=0.45, rely=rely, anchor="w", relwidth=0.18)
        year.place(relx=0.7, rely=rely, anchor="w", relwidth=0.19)
        return day, month, year

    def _time_controls(self, parent, rely):
        hours = [f"{i:02}" for i in range(24)]
        minutes = [f"{i:02}" for i in range(0, 60, 5)]
        hour = ttk.Combobox(parent, values=hours, state="readonly")
        minute = ttk.Combobox(parent, values=minutes, state="readonly")
        hour.set("00")
        minute.set("00")
        hour.place(relx=0.49, rely=rely, anchor="e", relwidth=0.15)
        minute.place(relx=0.52, rely=rely, anchor="w", relwidth=0.15)
        return hour, minute

    @staticmethod
    def _label(parent, text, rely):
        tk.Label(parent, text=text, font=("Arial", 13), bg=BG, fg=TEXT).place(relx=0.5, rely=rely, anchor="center")

    @staticmethod
    def _entry(parent, rely):
        entry = tk.Entry(parent, font=("Arial", 13), bg=BUTTON, fg=TEXT)
        entry.place(relx=0.5, rely=rely, anchor="center")
        return entry

    @staticmethod
    def _button(parent, text, command):
        button = tk.Button(parent, text=text, font=("Arial", 13, "bold"), bg=BUTTON, fg=TEXT, command=command)
        button.bind("<Enter>", lambda event: event.widget.config(bg=BUSY))
        button.bind("<Leave>", lambda event: event.widget.config(bg=BUTTON))
        return button

    def _read_datetime(self):
        target_date = datetime.strptime(
            f"{self.year_entry.get()}-{self.month_entry.get()}-{self.day_entry.get()}",
            "%Y-%m-%d",
        ).date()
        target_time = datetime.strptime(
            f"{self.hour_entry.get()}:{self.minute_entry.get()}",
            "%H:%M",
        ).time()
        return target_date, target_time

    def create_reservation(self):
        try:
            target_date, target_time = self._read_datetime()
            data = (
                self.name_entry.get(),
                self.phone_entry.get(),
                target_date,
                target_time,
                self.people_entry.get(),
                self.table_entry.get(),
            )
            self.reservation_service.validate(*data)
            if not messagebox.askyesno(
                "Επιβεβαίωση",
                f"Πρόκειται να δημιουργήσετε κράτηση:\n\n"
                f"Όνομα: {data[0]}\nΤηλέφωνο: {data[1]}\n"
                f"Ημερομηνία: {data[2]}\nΏρα: {data[3]}\n"
                f"Άτομα: {data[4]}\nΤραπέζι: {data[5].upper()}",
            ):
                return
            self.reservation_service.create(*data)
            self._clear_reservation_form()
            self.draw_tables()
        except (ValidationError, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την αποθήκευση: {exc}")

    def _clear_reservation_form(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.people_entry.delete(0, tk.END)
        self.table_entry.delete(0, tk.END)
        self._reset_date_controls()

    def _reset_date_controls(self):
        today = date.today()
        self.day_entry.set(f"{today.day:02}")
        self.month_entry.set(f"{today.month:02}")
        self.year_entry.set(str(today.year))
        self.hour_entry.set("00")
        self.minute_entry.set("00")

    def show_reservations(self):
        try:
            target_date = datetime.strptime(
                f"{self.show_year.get()}-{self.show_month.get()}-{self.show_day.get()}",
                "%Y-%m-%d",
            ).date()
            if target_date < date.today():
                raise ValidationError(f"Η Ημερομηνία Κράτησης δεν μπορεί να είναι πριν τη σημερινή {date.today()}")
            reservations = self.reservation_service.repository.list_for_date(target_date)
            self._reservation_window(target_date, reservations)
        except (ValidationError, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την ανάκτηση: {exc}")

    def _reservation_window(self, target_date, reservations):
        window = tk.Toplevel(self.root)
        window.title("Κρατήσεις")
        window.geometry("950x400")
        window.configure(bg=PANEL)
        tk.Label(
            window,
            text=f"Οι κρατήσεις για την ημερομηνία {target_date}",
            font=("Arial", 13, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).pack(pady=5, padx=10)
        tree = ttk.Treeview(
            window,
            columns=("table", "name", "phone", "time", "people", "change", "cancel"),
            show="headings",
        )
        tree.pack(fill="both", expand=True, pady=5, padx=10)
        for key, title, width in [
            ("table", "Τραπέζι", 100),
            ("name", "Ονοματεπώνυμο", 250),
            ("phone", "Τηλέφωνο", 150),
            ("time", "Ώρα", 100),
            ("people", "Άτομα", 100),
            ("change", "", 100),
            ("cancel", "", 100),
        ]:
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="center")
        for reservation in reservations:
            tree.insert(
                "",
                "end",
                iid=str(reservation.id),
                values=(
                    reservation.table_name,
                    reservation.name,
                    reservation.phone,
                    reservation.time.strftime("%H:%M"),
                    reservation.people,
                    "",
                    "",
                ),
            )
        for index, reservation in enumerate(reservations):
            y = 75 + index * 40
            tk.Button(
                window,
                text="Επεξεργασία",
                font=("Arial", 11),
                bg=PANEL,
                fg=TEXT,
                command=lambda r=reservation: self.edit_reservation(r, window),
            ).place(x=730, y=y, width=100, height=25)
            tk.Button(
                window,
                text="Ακύρωση",
                font=("Arial", 11),
                bg=PANEL,
                fg=TEXT,
                command=lambda r=reservation: self.cancel_reservation(r, window),
            ).place(x=835, y=y, width=100, height=25)

    def edit_reservation(self, reservation, parent):
        parent.destroy()
        window = tk.Toplevel(self.root)
        window.title("Επεξεργασία Κράτησης")
        window.geometry("500x700")
        window.configure(bg=PANEL)
        frame = tk.Frame(window, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        entries = []
        values = [
            ("Όνομα", reservation.name),
            ("Τηλέφωνο", reservation.phone),
            ("Άτομα", str(reservation.people)),
            ("Τραπέζι", reservation.table_name),
        ]
        for index, (label, value) in enumerate(values):
            tk.Label(frame, text=label, font=("Arial", 13), bg=BG, fg=TEXT).pack(pady=(10, 2))
            entry = tk.Entry(frame, font=("Arial", 13), bg=BUTTON, fg=TEXT)
            entry.insert(0, value)
            entry.pack()
            entries.append(entry)
        tk.Label(frame, text="Ημερομηνία (YYYY-MM-DD)", font=("Arial", 13), bg=BG, fg=TEXT).pack(pady=(10, 2))
        date_entry = tk.Entry(frame, font=("Arial", 13), bg=BUTTON, fg=TEXT)
        date_entry.insert(0, reservation.date.isoformat())
        date_entry.pack()
        tk.Label(frame, text="Ώρα (HH:MM)", font=("Arial", 13), bg=BG, fg=TEXT).pack(pady=(10, 2))
        time_entry = tk.Entry(frame, font=("Arial", 13), bg=BUTTON, fg=TEXT)
        time_entry.insert(0, reservation.time.strftime("%H:%M"))
        time_entry.pack()
        entries.extend([date_entry, time_entry])
        self._button(
            frame,
            "Αποθήκευση αλλαγών",
            lambda: self._save_edit(window, reservation.id, entries),
        ).pack(pady=25)

    def _save_edit(self, window, reservation_id, entries):
        try:
            target_date = datetime.strptime(entries[4].get(), "%Y-%m-%d").date()
            target_time = datetime.strptime(entries[5].get(), "%H:%M").time()
            self.reservation_service.update(
                reservation_id,
                entries[0].get(),
                entries[1].get(),
                target_date,
                target_time,
                entries[2].get(),
                entries[3].get(),
            )
            window.destroy()
            self.draw_tables()
            messagebox.showinfo("Επιτυχία", "Η επεξεργασία της κράτησης ολοκληρώθηκε με επιτυχία.")
        except (ValidationError, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
            window.focus_force()
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την αποθήκευση: {exc}")

    def cancel_reservation(self, reservation, parent):
        if not messagebox.askyesno(
            "Ακύρωση Κράτησης",
            f"Θέλετε να ακυρώσετε την κράτηση:\n\n"
            f"{reservation.table_name}\t{reservation.name}\t"
            f"{reservation.date}\t{reservation.time.strftime('%H:%M')}\t"
            f"{reservation.people} άτομα",
        ):
            return
        try:
            self.reservation_service.cancel(reservation.id)
            parent.destroy()
            self.draw_tables()
            messagebox.showinfo("Επιτυχία", "Η κράτηση ακυρώθηκε επιτυχώς.")
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την ακύρωση: {exc}")

    def new_table(self):
        window = tk.Toplevel(self.root)
        window.title("Νέο Τραπέζι")
        window.geometry("300x220")
        window.configure(bg=PANEL)
        tk.Label(window, text="Όνομα τραπεζιού", font=("Arial", 12), bg=PANEL, fg=TEXT).pack(pady=(10, 5))
        name = tk.Entry(window, font=("Arial", 12), bg=BUTTON, fg=TEXT)
        name.pack()
        tk.Label(window, text="Χωρητικότητα", font=("Arial", 12), bg=PANEL, fg=TEXT).pack(pady=(10, 5))
        capacity = tk.Entry(window, font=("Arial", 12), bg=BUTTON, fg=TEXT)
        capacity.pack()
        self._button(window, "Προσθήκη", lambda: self._add_table(name, capacity, window)).pack(pady=20)

    def _add_table(self, name, capacity, window):
        try:
            self.table_service.add(name.get(), capacity.get())
            window.destroy()
            self.refresh_tables()
        except ValidationError as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την προσθήκη: {exc}")

    def delete_table(self):
        window = tk.Toplevel(self.root)
        window.title("Κατάργηση τραπεζιού")
        window.geometry("300x200")
        window.configure(bg=PANEL)
        tk.Label(window, text="Όνομα τραπεζιού", font=("Arial", 12), bg=PANEL, fg=TEXT).pack(pady=(10, 5))
        name = tk.Entry(window, font=("Arial", 12), bg=BUTTON, fg=TEXT)
        name.pack()
        self._button(window, "Κατάργηση", lambda: self._delete_table(name, window)).pack(pady=25)

    def _delete_table(self, name, window):
        try:
            self.table_service.delete(name.get())
            window.destroy()
            self.refresh_tables()
        except ValidationError as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την κατάργηση: {exc}")

    def refresh_tables(self):
        self.tables = self.table_service.list_tables()
        self.table_sizes = {table.name: table.capacity for table in self.tables}
        self.draw_tables()

    def draw_tables(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        for item in self.status_buttons.values():
            item.destroy()
        self.status_buttons.clear()
        self.table_items.clear()
        self.tables = self.table_service.list_tables()
        self.table_sizes = {table.name: table.capacity for table in self.tables}
        width = max(self.canvas.winfo_width(), 880)
        x, y = 20, 20
        size = 125
        horizontal = 145
        large_horizontal = 185
        for table in self.tables:
            is_large = table.capacity > 4
            table_width = 175 if is_large else size
            table_id = (
                self.canvas.create_rectangle(x, y, x + table_width, y + size, fill=BUTTON, outline="white")
                if table.capacity >= 4
                else self.canvas.create_oval(x, y, x + size, y + size, fill=BUTTON, outline="white")
            )
            text_id = self.canvas.create_text(
                x + table_width / 2,
                y + size / 2,
                text=f"{table.name}\n {table.capacity}",
                font=("Arial", 10),
                fill="white",
            )
            self.table_items[table.name] = {
                "shape": table_id,
                "text": text_id,
                "x": x,
                "y": y,
                "width": table_width,
                "size": size,
            }
            button = tk.Button(
                self.canvas,
                text="Busy",
                font=("Arial", 9),
                bg=TEXT,
                fg=BUTTON,
                command=lambda name=table.name: self.toggle_manual_busy(name),
            )
            button.place(
                x=x + table_width * (0.35 if not is_large else 0.55),
                y=y + size * 0.75,
                width=40,
            )
            self.status_buttons[table.name] = button
            x += large_horizontal if is_large else horizontal
            if x + horizontal + 10 >= width:
                x = 20
                y += 145

    def toggle_manual_busy(self, table_name):
        if table_name in self.manual_busy:
            self.manual_busy.remove(table_name)
            self._set_table_status(table_name, False)
        else:
            self.manual_busy.add(table_name)
            self._set_table_status(table_name, True)

    def update_status(self):
        try:
            reservations = self.reservation_service.active_reservations()
            active = {reservation.table_name: reservation for reservation in reservations}
            for table in self.tables:
                reservation = active.get(table.name)
                if reservation:
                    label = (
                        f"   {table.name}\n"
                        f"{self._display_name(reservation.name)}\n"
                        f"{reservation.time.strftime('%H:%M')}\n"
                        f" {reservation.people} άτομα"
                    )
                    self._set_table_status(table.name, True, label)
                    button = self.status_buttons.get(table.name)
                    if button:
                        button.place_forget()
                elif table.name not in self.manual_busy:
                    self._set_table_status(table.name, False, f"{table.name}\n {table.capacity}")
                    self._place_status_button(table.name)
        except Exception as exc:
            messagebox.showerror("Error", f"Σφάλμα κατά την ενημέρωση κατάστασης: {exc}")
        finally:
            self.root.after(3000, self.update_status)

    def _display_name(self, name):
        parts = name.split()
        if len(parts) > 1:
            return f"{parts[1][:12]} {parts[0][0]}."
        return parts[0][:12]

    def _set_table_status(self, name, busy, text=None):
        item = self.table_items.get(name)
        if not item:
            return
        self.canvas.itemconfig(item["shape"], fill=BUSY if busy else BUTTON)
        self.canvas.itemconfig(item["text"], text=text or f"{name}\n {self.table_sizes.get(name, '')}")

    def _place_status_button(self, name):
        item = self.table_items.get(name)
        button = self.status_buttons.get(name)
        if not item or not button:
            return
        button.place(
            x=item["x"] + item["width"] * (0.35 if item["width"] <= 125 else 0.55),
            y=item["y"] + item["size"] * 0.75,
            width=40,
        )

    def _update_time(self):
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.root.after(1000, self._update_time)
