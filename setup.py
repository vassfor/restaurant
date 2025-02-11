from create_db import create_db
from create_tables import create_tables
import tkinter as tk
from tkinter import messagebox,ttk
import mysql.connector
import json


host = "localhost"
user = "root"
password = ""
database_name = "restaurant"


def add_tb_data(entries):
    json_read = open("business_data.json", "r",encoding="utf-8")
    data = json.load(json_read)
    connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database_name
    )
    cursor = connection.cursor()
    try:
        insert_data = []
        for name, cap in entries:
            tb_name = name.get().strip()
            tb_cap = cap.get().strip()
            if not tb_name:
                messagebox.showerror("Error", "Το Όνομα Τραπεζιού δεν μπορεί να είναι κενό")
                return
            if not tb_cap.isdigit():
                messagebox.showerror("Error", "Η χωρητικότητα πρέπει να είναι αριθμός")
                return
            for n,c in insert_data:
                if n.lower() == tb_name.lower():
                    messagebox.showerror("Error", f"Το Όνομα Τραπεζιού '{tb_name}' υπάρχει ήδη")
                    return
            insert_data.append((tb_name.upper(),int(tb_cap)))
        cursor.executemany(
            """INSERT INTO Tables(name, capacity)
                VALUES(%s,%s);""",
                insert_data
        )
        connection.commit()
        for tb in insert_data:
            data["tables"].append(tb)
        json_read.close()
        json_append = open("business_data.json", "w",encoding="utf-8")
        json.dump(data,json_append, ensure_ascii=False, indent=4)
        json_append.close()

        print("Data inserted into 'Tables' table of the database")
        result = messagebox.showinfo("Success", "Τα δεδομένα της επιχείρησής σας εισήχθησαν με επιτυχία!")
        if result == "ok":
            root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def tables(bsName, tableNo):
    if not bsName:
        messagebox.showerror("Error", "Το Όνομα Επιχείρησης δεν μπορεί να είναι κενό")
        return
    if not tableNo.isdigit():
        messagebox.showerror("Error", "Ο Αριθμός Τραπεζιών πρέπει να είναι αριθμός")
        return
    business_data = {
        "business_name": bsName,
        "table_no": tableNo,
        "tables": []
    }
    json_file = open("business_data.json","w",encoding="utf-8")
    json.dump(business_data,json_file,ensure_ascii=False,indent=4)
    json_file.close()

    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Παρακαλώ εισάγεται το όνομα κάθε τραπεζιού και τη χωρητικότητά του σε άτομα", font=("Arial", 13),bg="#17202A",fg="#EAECEE").pack(pady=10)
    table_frame=tk.Frame(root)
    table_frame.pack(pady=10)
    table_frame.configure(bg="#17202A")
    tk.Label(table_frame, text="Όνομα τραπεζιού", font=("Arial", 13),bg="#17202A",fg="#EAECEE").grid(row=0, column=0, padx=10, pady=8)
    tk.Label(table_frame, text="Χωρητικότητα", font=("Arial", 13),bg="#17202A",fg="#EAECEE").grid(row=0, column=1, padx=10, pady=8)
    
    global entries
    entries =[]
    for i in range(int(tableNo)):
        tb_name = tk.Entry(table_frame, font=("Arial", 13), bg="#2C3E50",fg = "#EAECEE", width=10)
        tb_name.grid(row=i+1, column=0, padx=10, pady=8)
        tb_cap =tk.Entry(table_frame, font=("Arial", 13), bg="#2C3E50",fg = "#EAECEE", width=10)
        tb_cap.grid(row=i+1, column=1, padx=10, pady=8)
        entries.append((tb_name, tb_cap))
    next_button = tk.Button(root, text = "Επόμενο", font=("Arial", 13), bg="#2C3E50",fg = "#EAECEE", command = lambda: add_tb_data(entries))
    next_button.pack(pady=10)
    next_button.bind("<Enter>", on_enter)
    next_button.bind("<Leave>", on_leave)

def start(start_button):
    start_button.destroy()
    name_lb = tk.Label(root, text="Όνομα Επιχείρησης:", font=("Arial", 15),bg="#17202A",fg="#EAECEE")
    name_lb.place(relx=0.5, rely=0.35, anchor="center")
    business_name = tk.Entry(root, font=("Arial", 15),bg="#2C3E50",fg = "#EAECEE")
    business_name.place(relx=0.5, rely=0.4, anchor="center")

    table_lb = tk.Label(root, text="Αριθμός Τραπεζιών:", font=("Arial", 15),bg="#17202A",fg="#EAECEE")
    table_lb.place(relx=0.5, rely=0.55, anchor="center")
    table_no = tk.Entry(root, font=("Arial", 15),bg="#2C3E50",fg = "#EAECEE")
    table_no.place(relx=0.5, rely=0.6, anchor="center")

    next_button = tk.Button(root, text = "Επόμενο", font=("Arial", 15), bg="#2C3E50",fg = "#EAECEE",command=lambda:tables(business_name.get(),table_no.get()))
    next_button.place(relx=0.5, rely=0.8, anchor="center")
    next_button.bind("<Enter>", on_enter)
    next_button.bind("<Leave>", on_leave)

def setup():
    create_db(host, user, password, database_name)
    create_tables(host, user, password, database_name)
    print("Database and tables setup is complete")

    global root
    root = tk.Tk()
    root.title("Setup page")
    root.geometry("800x600")
    root.configure(bg="#17202A")

    label = tk.Label(root, text="Καλωσήρθατε!", font=("Arial",25),bg="#17202A",fg="#EAECEE")
    label.place(relx=0.5, rely=0.2, anchor="center")

    start_button = tk.Button(root, text="Έναρξη", font=("Arial", 15), bg="#2C3E50",fg = "#EAECEE",command = lambda:start(start_button))
    start_button.place(relx=0.5, rely=0.5, anchor="center")
    start_button.bind("<Enter>", on_enter)
    start_button.bind("<Leave>", on_leave)
    root.mainloop()

def on_enter(event):
    event.widget.config(bg="#FF5733")

def on_leave(event):
    event.widget.config(bg="#2C3E50")
    
def on_enter2(event):
    event.widget.config(bg="#FF3B5C")
