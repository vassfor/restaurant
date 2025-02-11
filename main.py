import tkinter as tk
from tkinter import messagebox,ttk
import mysql.connector
import json
import os
from datetime import datetime,date,timedelta
from setup import setup, on_enter, on_enter2, on_leave

host = "localhost"
user = "root"
password = ""
database_name = "restaurant"

def main_app():
    global main
    main = tk.Tk()
    main.title("Σύστημα Διαχείρησης Κρατήσεων Εστιατορίου")
    main.geometry("1200x800")
    main.configure(bg="#17202A")
    json_read = open("business_data.json","r",encoding="utf-8")
    data = json.load(json_read)
    the_name = data["business_name"]
    global the_tb_no
    the_tb_no = data["table_no"]
    global the_tables
    the_tables = data["tables"]
    json_read.close()
    global items
    items ={}
    global busyfree
    busyfree = {}
    for tb in the_tables:
        busyfree[tb[0]] = 0

    brand = tk.Label(main,text=the_name+"   Reservations", font=("Arial", 25,"bold"),bg="#17202A",fg="#EAECEE")
    brand.pack(pady=(20,10))
    global loading
    loading = tk.Label(main, text="Loading...", font=("Arial", 15),bg="#17202A",fg="#FF5733")
    loading.place(x=550,y=90)
    
    global time_label
    time_label = tk.Label(main, text="", font=("Arial", 15),bg="#17202A",fg="#EAECEE")
    time_label.place(x=70,y=90)
    update_time()
    global canvas
    canvas = tk.Canvas(main, width=880, height=640, bg="#17202A")
    canvas.pack(pady=(10,10), padx=(20,0), side=tk.LEFT, expand=True, fill=tk.X)

    def on_resize(event):
        draw_tables()
    canvas.bind("<Configure>", on_resize)

    add_table_button = tk.Button(canvas, text="Νέο τραπέζι", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE", command=new_table)
    add_table_button.place(relx=0.4,rely=0.95, anchor="c")
    add_table_button.bind("<Enter>", on_enter2)
    add_table_button.bind("<Leave>", on_leave)
    rem_table_button = tk.Button(canvas, text="Κατάργηση τραπεζιού", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE", command=del_table)
    rem_table_button.place(relx=0.6,rely=0.95, anchor="c")
    rem_table_button.bind("<Enter>", on_enter2)
    rem_table_button.bind("<Leave>", on_leave)
    reservations = tk.Canvas(main, width=260, height=640, bg="#17202A")
    reservations.pack(pady=(10,10), padx=(10,20), side=tk.RIGHT)
    reservations.create_line(0,470,700,470,fill="white", width=3)

    onoma = tk.Label(reservations, text="Όνομα", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    onoma.place(relx=0.5, rely=0.05, anchor="center")
    onoma_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE")
    onoma_entry.place(relx=0.5, rely=0.1, anchor="center")
    tel = tk.Label(reservations, text="Τηλέφωνο", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    tel.place(relx=0.5, rely=0.15, anchor="center")
    tel_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE")
    tel_entry.place(relx=0.5, rely=0.2, anchor="center")
    rdate = tk.Label(reservations, text="Ημέρα     Μήνας    Έτος", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    rdate.place(relx=0.5, rely=0.25, anchor="c")
    global days,day_combobox,months, month_combobox, years, year_combobox,hours,hour_entry,mins,min_entry
    days = [f"{i:02}" for i in range(1, 32)]
    day_combobox = ttk.Combobox(reservations, values=days, state="readonly")
    day_combobox.set(days[date.today().day -1])
    day_combobox.place(relx=0.35, rely=0.3, anchor="e",relwidth=0.18)
    months = [f"{i:02}" for i in range(1, 13)]
    month_combobox = ttk.Combobox(reservations, values=months, state="readonly")
    month_combobox.set(months[date.today().month - 1]) 
    month_combobox.place(relx=0.45, rely=0.3, anchor="w", relwidth=0.18)
    current_y = date.today().year
    years = [f"{i}" for i in range(current_y,current_y+5)]
    year_combobox = ttk.Combobox(reservations, values=years, state="readonly")
    year_combobox.set(years[0]) 
    year_combobox.place(relx=0.7, rely=0.3, anchor="w", relwidth=0.19)
    hours = [f"{i:02}" for i in range(0,24)]
    mins = [f"{i:02}" for i in range(0,60,5)]
    time = tk.Label(reservations, text="Ώρα", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    time.place(relx=0.5,rely=0.35, anchor="c")
    hour_entry = ttk.Combobox(reservations, values=hours, state="readonly")
    hour_entry.set(hours[0])
    hour_entry.place(relx=0.49, rely=0.4, anchor="e", relwidth=0.15)
    min_entry = ttk.Combobox(reservations, values=mins, state="readonly")
    min_entry.set(mins[0])
    min_entry.place(relx=0.52, rely=0.4, anchor="w", relwidth=0.15)
    people = tk.Label(reservations, text="Άτομα", font=("Arial", 13), bg="#17202A",fg="#EAECEE")
    people.place(relx=0.5, rely=0.45, anchor="c")
    people_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE")
    people_entry.place(relx=0.5, rely=0.5, anchor="c")
    sel_table = tk.Label(reservations, text="Τραπέζι", font=("Arial", 13), bg="#17202A",fg="#EAECEE")
    sel_table.place(relx=0.5, rely=0.55, anchor="c")
    sel_table_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE")
    sel_table_entry.place(relx=0.5, rely=0.6, anchor="c")
    res_entries = [onoma_entry,tel_entry,day_combobox,month_combobox,year_combobox,hour_entry,min_entry,people_entry, sel_table_entry]   

    reserve_button= tk.Button(reservations, text = "Νέα κράτηση", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE", command=lambda:reserve(res_entries))
    reserve_button.place(relx=0.5, rely=0.68, anchor="center")
    reserve_button.bind("<Enter>", on_enter)
    reserve_button.bind("<Leave>", on_leave)
    
    sdate = tk.Label(reservations, text="Ημέρα     Μήνας    Έτος", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    sdate.place(relx=0.5, rely=0.8, anchor="c")
    day2_combobox = ttk.Combobox(reservations, values=days, state="readonly")
    day2_combobox.set(days[date.today().day -1])
    day2_combobox.place(relx=0.35, rely=0.85, anchor="e",relwidth=0.18)
    month2_combobox = ttk.Combobox(reservations, values=months, state="readonly")
    month2_combobox.set(months[date.today().month - 1]) 
    month2_combobox.place(relx=0.45, rely=0.85, anchor="w", relwidth=0.18)
    year2_combobox = ttk.Combobox(reservations, values=years, state="readonly")
    year2_combobox.set(years[0]) 
    year2_combobox.place(relx=0.7, rely=0.85, anchor="w", relwidth=0.19)
    show_entries = [day2_combobox,month2_combobox,year2_combobox]
    show = tk.Button(reservations, text = "Εμφάνιση κρατήσεων", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE",command=lambda:show_res(show_entries))
    show.place(relx=0.5, rely=0.95, anchor="center")
    show.bind("<Enter>", on_enter2)
    show.bind("<Leave>", on_leave)
    main.after(200,draw_tables)
    main.after(2000,update_status)

    main.mainloop()

def update_res(window, tbid, entries):
    current_date = date.today()
    current_time = datetime.now().time()
    current_time = current_time.replace(second=0,microsecond=0)

    updated_data=[]
    id=tbid
    onoma = entries[0].get()
    tel = entries[1].get()
    day = entries[2].get()
    month = entries[3].get()
    year = entries[4].get()
    rdate = str(year)+"-"+str(month)+"-"+str(day)
    rdate = datetime.strptime(rdate, "%Y-%m-%d").date()
    hour = entries[5].get()
    min = entries[6].get()
    rtime = str(hour)+":"+str(min)
    rtime = datetime.strptime(rtime, "%H:%M").time()
    people = entries[7].get()
    selTb = entries[8].get()
    if not onoma:
        messagebox.showerror("Error", "Το Όνομα Πελάτη δεν μπορεί να είναι κενό")
        return
    if tel:
        if not tel.isdigit() or len(tel)!= 10:
            messagebox.showerror("Error", "Το Τηλέφωνο Πελάτη πρέπει να αποτελείται από 10 ψηφία")
            window.focus_force()
            return
    if rdate < current_date:
        messagebox.showerror("Error", f"Η Ημερομηνία Κράτησης δεν μπορεί να είναι πριν τη σημερινή {current_date}")
        window.focus_force()
        return
    elif rdate == current_date:
        if rtime < current_time:
            messagebox.showerror("Error", f"Η Ώρα Κράτησης για την τρέχουσα ημερομηνία δεν μπορεί να είναι πριν την τρέχουσα ώρα {current_time}")
            window.focus_force()
            return
    if (not people.isdigit()) or int(people)<=0:
        messagebox.showerror("Error", f"Ο Αριθμός Ατόμων πρέπει να είναι θετικός αριθμός")
        window.focus_force()
        return
    found = False
    for tb,c in the_tables:
        if tb.lower() == selTb.lower():
            found = True
    if not found:
        messagebox.showerror("Error", "Επιλέξτε διαθέσιμο τραπέζι")
        window.focus_force()
        return
    updated_data = [selTb.upper(),onoma,tel,rdate,rtime,int(people),id]

    try:
        connection = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database_name
        )
        cursor = connection.cursor()
        cursor.execute(
            """UPDATE Reservations
                SET table_name=%s,name=%s,phone=%s,date=%s,time=%s,people=%s
                WHERE id=%s;
            """,
            updated_data
        )
        connection.commit()
        window.destroy()
        draw_tables()
        messagebox.showinfo("Επιτυχία", "Η επεξεργασία της κράτησης ολοκληρώθηκε με επιτυχία.")
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def ch_res(date,info,window):
    global years,months,days,hours,mins
    window.destroy()
    id = info[0]
    tb = info[1]
    n = info[2]
    dtday = f"{date.day:02}"
    dtmon = f"{date.month:02}"
    dtyear = date.year
    ph = str(info[3])
    seconds = info[4].seconds
    hrs = seconds // 3600
    minutes = f"{((seconds % 3600) // 60 ):02}"
    seconds = f"{(seconds % 60):02}"
    p = str(info[5])
    change_win = tk.Toplevel()
    change_win.title("Επεξεργασία Κράτησης")
    change_win.geometry("500x700")
    change_win.configure(bg="#64727A")
    change_win.focus_force()
    text = tk.Label(change_win,text="Επεξεργασία της κράτησης με στοιχεία: ",font=("Arial", 13,"bold"), bg="#64727A",fg = "#EAECEE")
    text.pack(pady=5,padx=10)

    reservations = tk.Canvas(change_win, width=450, height=580, bg="#17202A")
    reservations.pack(pady=(10,10), padx=(10,20), side=tk.TOP)

    onoma = tk.Label(reservations, text="Όνομα", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    onoma.place(relx=0.5, rely=0.05, anchor="center")
    onoma_var = tk.StringVar()
    onoma_var.set(n)
    onoma_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE",textvariable=onoma_var)
    onoma_entry.place(relx=0.5, rely=0.1, anchor="center")

    tel = tk.Label(reservations, text="Τηλέφωνο", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    tel.place(relx=0.5, rely=0.15, anchor="center")
    tel_var = tk.StringVar()
    tel_var.set(ph)
    tel_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE",textvariable=tel_var)
    tel_entry.place(relx=0.5, rely=0.2, anchor="center")

    rdate = tk.Label(reservations, text="Ημέρα     Μήνας    Έτος", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    rdate.place(relx=0.5, rely=0.25, anchor="c")
    day_combobox = ttk.Combobox(reservations, values=days, state="readonly")
    day_combobox.set(dtday)
    day_combobox.place(relx=0.35, rely=0.3, anchor="e",relwidth=0.18)
    month_combobox = ttk.Combobox(reservations, values=months, state="readonly")
    month_combobox.set(dtmon) 
    month_combobox.place(relx=0.45, rely=0.3, anchor="w", relwidth=0.18)
    year_combobox = ttk.Combobox(reservations, values=years, state="readonly")
    year_combobox.set(dtyear) 
    year_combobox.place(relx=0.7, rely=0.3, anchor="w", relwidth=0.19)

    time = tk.Label(reservations, text="Ώρα", font=("Arial", 13),bg="#17202A",fg="#EAECEE")
    time.place(relx=0.5,rely=0.35, anchor="c")
    hour_entry = ttk.Combobox(reservations, values=hours, state="readonly")
    hour_entry.set(hrs)
    hour_entry.place(relx=0.49, rely=0.4, anchor="e", relwidth=0.15)
    min_entry = ttk.Combobox(reservations, values=mins, state="readonly")
    min_entry.set(minutes)
    min_entry.place(relx=0.52, rely=0.4, anchor="w", relwidth=0.15)

    people = tk.Label(reservations, text="Άτομα", font=("Arial", 13), bg="#17202A",fg="#EAECEE")
    people.place(relx=0.5, rely=0.45, anchor="c")
    people_var = tk.StringVar()
    people_var.set(p)
    people_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE",textvariable=people_var)
    people_entry.place(relx=0.5, rely=0.5, anchor="c")

    sel_table = tk.Label(reservations, text="Τραπέζι", font=("Arial", 13), bg="#17202A",fg="#EAECEE")
    sel_table.place(relx=0.5, rely=0.55, anchor="c")
    tb_var = tk.StringVar()
    tb_var.set(tb)
    sel_table_entry = tk.Entry(reservations, font=("Arial", 13),bg="#2C3E50",fg = "#EAECEE",textvariable=tb_var)
    sel_table_entry.place(relx=0.5, rely=0.6, anchor="c")

    res_entries = [onoma_entry,tel_entry,day_combobox,month_combobox,year_combobox,hour_entry,min_entry,people_entry, sel_table_entry]   
    
    reserve_button= tk.Button(reservations, text = "Αποθήκευση αλλαγών", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE",
                    command=lambda:update_res(change_win,id,res_entries))
    reserve_button.place(relx=0.5, rely=0.8, anchor="center")
    reserve_button.bind("<Enter>", on_enter)
    reserve_button.bind("<Leave>", on_leave)

def del_res(date,info,window):
    window.destroy()
    id = info[0]
    tb = info[1]
    n = info[2]
    dt = str(date)
    seconds = info[4].seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    tm = f"{hours:02}:{minutes:02}:{seconds:02}"
    p = str(info[5])
    yes = messagebox.askyesno("Ακύρωση Κράτησης", "Θέλετε να ακυρώσετε την κράτηση:\n\n"+tb+"\t"+n+"\t\t"+dt+"\t"+tm+"\t"+p+"άτομα")
    if yes:
        try:  
            connection = mysql.connector.connect(
                host = host,
                user = user,
                password = password,
                database = database_name
            )
            cursor = connection.cursor()
            cursor.execute(
                """DELETE FROM Reservations WHERE
                id = %s;
                """,
                (id,)
            )
            connection.commit()
            change_tb_color(tb,color="blue")
            capp=""
            for i in range(len(the_tables)):
                if the_tables[i][0].upper()==tb.upper():
                    capp=the_tables[i][1]
                    break
            new_txt = tb+"\n "+str(capp)
            change_tb_text(tb,new_txt)
            free_btns[tb].destroy()
            x = btn_items[tb]["x"]
            y = btn_items[tb]["y"]
            r1 = btn_items[tb]["r1"]
            if btn_items[tb]["shape"]<=4:
                btn_items[tb]["button"].place(x=x+r1*0.35,y=y+r1*0.75,width=40)
            else:
                btn_items[tb]["button"].place(x=x+r1*0.55,y=y+r1*0.75,width=40)
            busyfree[tb]=0
            print(busyfree)
            messagebox.showinfo("Επιτυχία", "Η κράτηση ακυρώθηκε επιτυχώς.")
        except Exception as e:
            messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

def show_res(entries):
    current_date = date.today()
    try:
        day = entries[0].get()
        month = entries[1].get()
        year = entries[2].get()
        rdate = str(year)+"-"+str(month)+"-"+str(day)
        rdate = datetime.strptime(rdate, "%Y-%m-%d").date()
        if rdate < current_date:
            messagebox.showerror("Error", f"Η Ημερομηνία Κράτησης δεν μπορεί να είναι πριν τη σημερινή {current_date}")
            return
        connection = mysql.connector.connect(
                host = host,
                user = user,
                password = password,
                database = database_name
                )
        cursor = connection.cursor()
        cursor.execute(
            """SELECT id,table_name,name,phone,time,people FROM reservations
                WHERE date = %s; """,
                (rdate,)
        )
        date_res_info = cursor.fetchall()
        date_res = [t[1:] for t in date_res_info]
        show_window = tk.Toplevel()
        show_window.title("Κρατήσεις")
        show_window.geometry("950x400")
        show_window.configure(bg="#64727A")
        text = tk.Label(show_window,text="Οι κρατήσεις για την ημερομηνία "+str(rdate),font=("Arial", 13,"bold"), bg="#64727A",fg = "#EAECEE")
        text.pack(pady=5,padx=10)

        style = ttk.Style()
        style.configure("Custom.Treeview",rowheight=40,background="#64727A",fieldbackground="#64727A",foreground="#EAECEE",font=("Arial", 11))
        style.configure("Custom.Treeview.Heading",background="#64727A",foreground="#64727A",font=("Arial", 12, "bold"))

        tree = ttk.Treeview(show_window, columns=("table","name","phone","time","people","change","cancel"),show="headings",style="Custom.Treeview")
        tree.pack(fill="both",expand=True,pady=5,padx=10)
        tree.heading("table",text="Τραπέζι")
        tree.heading("name",text="Ονοματεπώνυμο")
        tree.heading("phone",text="Τηλέφωνο")
        tree.heading("time",text="Ώρα")
        tree.heading("people",text="Άτομα")
        tree.heading("change",text="    ")
        tree.heading("cancel",text="    ")
        tree.column("table", width=100, anchor="center")
        tree.column("name", width=250, anchor="center")
        tree.column("phone", width=150, anchor="center")
        tree.column("time", width=100, anchor="center")
        tree.column("people", width=100, anchor="center")
        tree.column("change", width=100, anchor="center")
        tree.column("cancel", width=100, anchor="center")

        for r in date_res:
            full_row=r+("", "")
            tree.insert("","end",values=full_row)
        x=730
        x1=835
        y=75
        step = 40
        for i in range(len(date_res)):
            tk.Button(show_window,text="Επεξεργασία",font=("Arial", 11),bg="#64727A",fg = "#EAECEE",command=lambda i=i:ch_res(rdate,date_res_info[i],show_window)).place(x=x,y=y,width=100,height=25)
            tk.Button(show_window,text="Ακύρωση",font=("Arial", 11),bg="#64727A",fg = "#EAECEE",command=lambda i=i:del_res(rdate,date_res_info[i],show_window)).place(x=x1,y=y,width=100,height=25)
            y+=step
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def reserve(entries):
    current_date = date.today()
    current_time = datetime.now().time()
    current_time = current_time.replace(second=0,microsecond=0)
    try:
        insert_data = []
        onoma = entries[0].get()
        tel = entries[1].get()
        day = entries[2].get()
        month = entries[3].get()
        year = entries[4].get()
        rdate = str(year)+"-"+str(month)+"-"+str(day)
        rdate = datetime.strptime(rdate, "%Y-%m-%d").date()
        hour = entries[5].get()
        min = entries[6].get()
        rtime = str(hour)+":"+str(min)
        rtime = datetime.strptime(rtime, "%H:%M").time()
        people = entries[7].get()
        selTb = entries[8].get()
        if not onoma:
            messagebox.showerror("Error", "Το Όνομα Πελάτη δεν μπορεί να είναι κενό")
            return
        if tel:
            if not tel.isdigit() or len(tel)!= 10:
                messagebox.showerror("Error", "Το Τηλέφωνο Πελάτη πρέπει να αποτελείται από 10 ψηφία")
                return
        if rdate < current_date:
            messagebox.showerror("Error", f"Η Ημερομηνία Κράτησης δεν μπορεί να είναι πριν τη σημερινή {current_date}")
            return
        elif rdate == current_date:
            if rtime < current_time:
                messagebox.showerror("Error", f"Η Ώρα Κράτησης για την τρέχουσα ημερομηνία δεν μπορεί να είναι πριν την τρέχουσα ώρα {current_time}")
                return
        if (not people.isdigit()) or int(people)<=0:
            messagebox.showerror("Error", f"Ο Αριθμός Ατόμων πρέπει να είναι θετικός αριθμός")
            return
        found = False
        for tb,c in the_tables:
            if tb.upper() == selTb.upper():
                found = True
        if not found:
            messagebox.showerror("Error", "Επιλέξτε διαθέσιμο τραπέζι")
            return
        insert_data = [selTb.upper(),onoma,tel,rdate,rtime,int(people)]
        accept = tk.Toplevel()
        accept.title("Επιβεβαίωση")
        accept.geometry("400x300")
        accept.configure(bg="#64727A")
        text = tk.Label(accept,text="Πρόκειται να δημιουργήσετε κράτηση με τα εξής στοιχεία:", font=("Arial", 12), bg="#64727A",fg = "#EAECEE")
        text2 = tk.Label(accept,text="Όνομα: "+"\nΤηλέφωνο:    "+"\nΗμερομηνία:    "+"\nΏρα: "
                        +"\nΆτομα:    "+"\nΤραπέζι:  ", font=("Arial", 12), bg="#64727A",fg = "#EAECEE")
        text3 = tk.Label(accept,text=str(onoma)+"\n"+str(tel)+"\n"+str(rdate)+"\n"+str(rtime)+"\n"+str(people)+"\n"+str(selTb), font=("Arial", 12), bg="#64727A",fg = "#EAECEE")
        text.pack(fill="x", pady=10)
        text2.place(relx=0.35, rely=0.5, anchor="center")
        text3.place(relx=0.65, rely=0.5, anchor="center")

        def accept_clicked():
            try:
                connection = mysql.connector.connect(
                host = host,
                user = user,
                password = password,
                database = database_name
                )
                cursor = connection.cursor()
                cursor.execute(
                """INSERT INTO Reservations(table_name, name, phone, date, time, people)
                    VALUES(%s,%s,%s,%s,%s,%s);""",
                    insert_data
                )
                connection.commit()
                accept.destroy()
                for e in entries:
                    e.delete(0,tk.END)
                year_combobox.set(years[0])
                month_combobox.set(months[date.today().month -1])
                day_combobox.set(days[date.today().day -1])
                min_entry.set(mins[0])
                hour_entry.set(hours[0])
            except Exception as e:
                messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()

        def cancel_clicked():
            accept.destroy()
            return
            
        accept_btn = tk.Button(accept, text="Επιβεβαίωση", font=("Arial", 13), bg="#2C3E50",fg = "#EAECEE", command=accept_clicked)
        accept_btn.place(relx=0.35, rely=0.9, anchor="center")
        cancel_btn = tk.Button(accept, text="Ακύρωση", font=("Arial", 13) , bg="#2C3E50",fg = "#EAECEE", command=cancel_clicked)
        cancel_btn.place(relx=0.65, rely=0.9, anchor="center")
        accept_btn.bind("<Enter>", on_enter)
        accept_btn.bind("<Leave>", on_leave)
        cancel_btn.bind("<Enter>", on_enter2)
        cancel_btn.bind("<Leave>", on_leave)
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")

def rem_table(name,window):
    json_read = open("business_data.json","r",encoding="utf-8")
    data = json.load(json_read)
    json_read.close()
    connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database_name
    )
    cursor = connection.cursor()
    try:
        global the_tables, the_tb_no
        found = False
        for tb,c in the_tables:
            if tb.lower() == name.lower():
                found = True
        if not found:
            messagebox.showerror("Error", "Επιλέξτε διαθέσιμο τραπέζι")
            window.destroy()
            return
        else:
            print("found: "+name)
            cursor.execute(
                """DELETE FROM Tables WHERE name = %s;""",
                (name,)
            )
            connection.commit()
            for tb in data["tables"]:
                if tb[0].lower() == name.lower():
                    data["tables"].remove(tb)
                    data["table_no"] = str(int(data["table_no"])-1)
            json_append = open("business_data.json", "w",encoding="utf-8")
            json.dump(data,json_append, ensure_ascii=False, indent=4)
            json_append.close()
            the_tables = data["tables"]
            the_tb_no=str(int(the_tb_no)-1)
            window.destroy()
            draw_tables()
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def del_table():
    remTb = tk.Toplevel()
    remTb.title("Κατάργηση τραπεζιού")
    remTb.geometry("300x200")
    remTb.configure(bg="#64727A")
    
    n = tk.Label(remTb, text="Όνομα τραπεζιού", font=("Arial", 12), bg="#64727A",fg = "#EAECEE")
    n.pack(pady=(5,5))
    ne = tk.Entry(remTb, font=("Arial", 12), bg="#2C3E50",fg = "#EAECEE")
    ne.pack(pady=(0,0))

    del_button = tk.Button(remTb, text="Κατάργηση", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE", command=lambda:rem_table(ne.get(),remTb))
    del_button.pack(pady=(25,0))
    del_button.bind("<Enter>", on_enter)
    del_button.bind("<Leave>", on_leave)

def add_new_tb(n,c,window):
    json_read = open("business_data.json","r",encoding="utf-8")
    data = json.load(json_read)
    json_read.close()
    connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database_name
    )
    cursor = connection.cursor()
    try:
        if not n:
            messagebox.showerror("Error", "Το Όνομα Τραπεζιού δεν μπορεί να είναι κενό")
            return
        if not c.isdigit():
            messagebox.showerror("Error", "Η χωρητικότητα πρέπει να είναι αριθμός")
            return
        for nam,cap in data["tables"]:
            if nam.lower() == n.lower():
                messagebox.showerror("Error", "Το Όνομα Τραπεζιού υπάρχει ήδη")
                return
        data["tables"].append([n,int(c)])
        data["table_no"] = str(int(data["table_no"])+1)
        cursor.execute(
            """INSERT INTO Tables(name, capacity)
                VALUES(%s,%s);""",
                (n,c)
        )
        connection.commit()
        print("Data inserted into 'Tables' table of the database")
        json_append = open("business_data.json", "w",encoding="utf-8")
        json.dump(data,json_append, ensure_ascii=False, indent=4)
        json_append.close()
        global the_tables, the_tb_no
        the_tables = data["tables"]
        the_tb_no=str(int(the_tb_no)+1)
        window.destroy()
        draw_next_tb()
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def new_table():
    newTb = tk.Toplevel()
    newTb.title("Νέο Τραπέζι")
    newTb.geometry("300x200")
    newTb.configure(bg="#64727A")
    
    n = tk.Label(newTb, text="Όνομα τραπεζιού", font=("Arial", 12), bg="#64727A",fg = "#EAECEE")
    n.pack(pady=(5,5))
    ne = tk.Entry(newTb, font=("Arial", 12), bg="#2C3E50",fg = "#EAECEE")
    ne.pack(pady=(0,0))
    c = tk.Label(newTb, text="Χωρητικότητα", font=("Arial", 12), bg="#64727A",fg = "#EAECEE")
    c.pack(pady=(10,5))
    ce = tk.Entry(newTb, font=("Arial", 12), bg="#2C3E50",fg = "#EAECEE")
    ce.pack(pady=(0,0))

    add_button = tk.Button(newTb, text="Προσθήκη", font=("Arial", 13, "bold"), bg="#2C3E50",fg = "#EAECEE", command=lambda:add_new_tb(ne.get(),ce.get(),newTb))
    add_button.pack(pady=(25,0))
    add_button.bind("<Enter>", on_enter)
    add_button.bind("<Leave>", on_leave)

free_btns={}
def update_status():
    current_date = date.today()
    current_time = datetime.now().time()
    current_time = current_time.replace(second=0,microsecond=0)
    pre_time = datetime.now().replace(second=0,microsecond=0) - timedelta(hours=2, minutes=0)
    pre_time = pre_time.time()
    after_time = datetime.now().replace(second=0,microsecond=0) + timedelta(hours=2, minutes=0)
    after_time = after_time.time()

    connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database_name
    )
    cursor1 = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    try:
        cursor1.execute(
            """SELECT t.* FROM tables t
                JOIN reservations r on t.name = r.table_name 
                WHERE date=%s AND time <= %s OR time >= %s;""",
                (current_date,pre_time,after_time)
        )
        rem = cursor1.fetchall()
        for t,c in rem:
            change_tb_color(t,color="blue")
            new_txt = t+"\n "+str(c)
            change_tb_text(t,new_txt)
            free_btns[t].destroy()
            x = btn_items[t]["x"]
            y = btn_items[t]["y"]
            r1 = btn_items[t]["r1"]
            if btn_items[t]["shape"]<=4:
                btn_items[t]["button"].place(x=x+r1*0.35,y=y+r1*0.75,width=40)
            else:
                btn_items[t]["button"].place(x=x+r1*0.55,y=y+r1*0.75,width=40)
            busyfree[t]=0 
        cursor2.execute(
            """DELETE FROM reservations 
                WHERE date<%s OR(date=%s AND time <= %s);""",
                (current_date,current_date,pre_time)
        )
        connection.commit()
        cursor3.execute(
            """SELECT id,table_name,name,time,people FROM reservations
                WHERE date=%s AND time BETWEEN %s AND %s;""",
                (current_date,pre_time,after_time)
        )
        res = cursor3.fetchall()
        for i,t,n,tm,p in res:
            id=i
            t=t.upper()
            change_tb_color(t)
            seconds = tm.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            tm = f"{hours:02}:{minutes:02}:{seconds:02}"
            full_n = n.split(" ")
            if len(full_n) > 1:
                if len(full_n[1])>12:
                    n = full_n[1][0:12] +". "+ full_n[0][0]+"."
                else:
                    n = full_n[1] +" "+ full_n[0][0]+"."
            else:
                n=full_n[0]
            new_t = "   "+t+"\n"+n+"\n"+tm+"\n "+str(p)+" άτομα"
            change_tb_text(t,new_t)
            btn_items[t]["button"].place_forget()
            free = tk.Button(canvas,text="Free",font=("Arial", 9),  bg="#EAECEE",fg ="#2C3E50", command=lambda id=id,t=t:free_res(free,t,id))
            free_btns[t]=free
            x=btn_items[t]["x"]
            y=btn_items[t]["y"]
            r1=btn_items[t]["r1"]
            if btn_items[t]["shape"]<=4:
                free.place(x=x+r1*0.35,y=y+r1*0.75,width=40)
            else:
                free.place(x=x+r1*0.55,y=y+r1*0.75,width=40)
            busyfree[t]=1
            print(busyfree)
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor1.close()
        cursor2.close()
        connection.close()
    main.after(3000, update_status)

def free_res(btn1,t,id):
    try:  
        connection = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database_name
        )
        cursor = connection.cursor()
        cursor.execute(
            """DELETE FROM Reservations WHERE
            id = %s;
            """,
            (id,)
        )
        connection.commit()
        change_tb_color(t,color="blue")
        new_txt = t+"\n "+str(btn_items[t]["shape"])
        change_tb_text(t,new_txt)
        busyfree[t] = 0
        print(busyfree)
        btn1.destroy()
        x = btn_items[t]["x"]
        y = btn_items[t]["y"]
        r1 = btn_items[t]["r1"]
        if btn_items[t]["shape"]<=4:
            btn_items[t]["button"].place(x=x+r1*0.35,y=y+r1*0.75,width=40)
        else:
            btn_items[t]["button"].place(x=x+r1*0.55,y=y+r1*0.75,width=40)            
    except Exception as e:
        messagebox.showerror("Error", f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def change_tb_color(tb_name, color="orange"):
    global items
    color_dict = {
        "blue":"#2C3E50",
        "orange":"#FF5733"
    }
    new_color = color_dict[color]
    if tb_name in items:
        table_id = items[tb_name]["shape"]
        canvas.itemconfig(table_id,fill=new_color)
    else:
        print("ERROR")
                
def change_tb_text(tb_name, new_text):
    global items
    if tb_name in items:
        text_id = items[tb_name]["text"]
        canvas.itemconfig(text_id, text=new_text, font=("Arial", 10))
    else:
        print("ERROR")

btn_items = {}
def draw_tables():
    canvas.delete("all")
    for key in list(btn_items.keys()):
        btn_items[key]["button"].destroy()
    for key in list(free_btns.keys()):
        free_btns[key].destroy()
    global x,y,i
    x,y=20,20
    i=0
    r1=125
    r2=175
    r3=145
    r4=185

    global draw_next_tb
    def draw_next_tb():
        global x,y,i,items
        nonlocal r1,r2,r3,r4
        if i>=len(the_tables):
            loading.destroy()
            return 
        if the_tables[i][1]<4:
            table_id = canvas.create_oval(x, y, x+r1, y+r1, fill="#2C3E50", outline="white", width=1)
            text_id = canvas.create_text(x + r1/2, y + r1/2, text=the_tables[i][0]+"\n "+str(the_tables[i][1]), font=("Arial", 10), fill="white")
            btn = tk.Button(canvas,text="Busy",font=("Arial", 9),  bg="#EAECEE",fg ="#2C3E50",command=lambda i=i:busytb(the_tables[i][0]))
            btn.place(x=x+r1*0.35,y=y+r1*0.75)
            btn_items[the_tables[i][0]]={"button":btn,"shape":the_tables[i][1],"x":x,"y":y,"r1":r1}
            x+=r3
        elif the_tables[i][1]==4:
            table_id = canvas.create_rectangle(x, y, x+r1, y+r1, fill="#2C3E50", outline="white", width=1)
            text_id = canvas.create_text(x + r1/2, y + r1/2, text=the_tables[i][0]+"\n "+str(the_tables[i][1]), font=("Arial", 10), fill="white")
            btn = tk.Button(canvas,text="Busy",font=("Arial", 9),  bg="#EAECEE",fg ="#2C3E50",command=lambda i=i:busytb(the_tables[i][0]))
            btn.place(x=x+r1*0.35,y=y+r1*0.75)
            btn_items[the_tables[i][0]]={"button":btn,"shape":the_tables[i][1],"x":x,"y":y,"r1":r1}
            x+=r3
        else:
            table_id = canvas.create_rectangle(x, y, x+r2, y+r1, fill="#2C3E50", outline="white", width=1)
            text_id = canvas.create_text(x + r2/2, y + r1/2, text=the_tables[i][0]+"\n "+str(the_tables[i][1]), font=("Arial", 10), fill="white")
            btn = tk.Button(canvas,text="Busy",font=("Arial", 9),  bg="#EAECEE",fg ="#2C3E50",command=lambda i=i:busytb(the_tables[i][0]))
            btn.place(x=x+r1*0.55,y=y+r1*0.75)
            btn_items[the_tables[i][0]]={"button":btn,"shape":the_tables[i][1],"x":x,"y":y,"r1":r1}
            x+=r4           
        items[the_tables[i][0]] = {"shape":table_id,"text":text_id}
        if x+r3+10>=canvas.winfo_width():
            x=20
            y+=r3
        if y+r3+10>=canvas.winfo_height():
            canvas.delete("all")
            x, y = 20, 20
            i=-1
            r1=r1*0.85
            r2=r2*0.85
            r3=r3*0.85
            r4=r4*0.85
        
        i+=1
        main.after(100,draw_next_tb)

    draw_next_tb()

def freetb(btn,n):
    change_tb_color(n,"blue")
    btn.destroy()
    busyfree[n] = 0
    print(busyfree)

def busytb(n):
    shape = btn_items[n]["shape"]
    x = btn_items[n]["x"]
    y = btn_items[n]["y"]
    r1 = btn_items[n]["r1"]
    change_tb_color(n)
    if shape<=4:
        freebtn = tk.Button(canvas,text="Free",font=("Arial", 9),  bg="#EAECEE",fg ="#2C3E50", command=lambda n=n:freetb(freebtn,n))
        freebtn.place(x=x+r1*0.35,y=y+r1*0.75,width=40)
        busyfree[n] = 1
        print(busyfree)
    else:
        freebtn = tk.Button(canvas,text="Free",font=("Arial", 9),  bg="#EAECEE",fg ="#2C3E50", command=lambda n=n:freetb(freebtn,n))
        freebtn.place(x=x+r1*0.55,y=y+r1*0.75,width=40)
        busyfree[n] = 1
        print(busyfree)

def update_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    time_label.config(text=current_time)
    main.after(1000,update_time)

if os.path.exists("business_data.json"):
    main_app()
else:
    setup()
    main_app()