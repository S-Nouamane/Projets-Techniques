import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import serial

# Create the main window
fenetre = tk.Tk()
fenetre.geometry("800x800")
bg = "#99D9EA"
fenetre.configure(bg=bg)

# Calculate the coordinates to center the window on the screen
largeur_ecran = fenetre.winfo_screenwidth()
hauteur_ecran = fenetre.winfo_screenheight()
x = (largeur_ecran - 700) // 2
y = (hauteur_ecran - 700) // 2

# Position the window at the center of the screen
fenetre.geometry(f"700x700+{x}+{y}")

def afficher_adherent_et_repas(id, fenetre):
    try:
        # Connect to the database
        conn = sqlite3.connect('sqlite_TIPE.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return

    cur.execute("SELECT * FROM adherent WHERE id=?", (id,))
    adherent = cur.fetchone()

    if adherent is None:
        print(f"Aucun adhérent trouvé avec cet ID: '{id}'")
        conn.close()
        return

    print(f"ID détecté: '{id}'")

    # Clear the previous contents of the window
    for widget in fenetre.winfo_children():
        widget.destroy()

    # Create a frame to group the adherent and repas information
    frame_principal = tk.Frame(fenetre, bg=bg)
    frame_principal.pack(expand=True, fill="both")

    # Add a title label
    label_titre = tk.Label(frame_principal, text="Informations de l'adhérent et du repas", font=("Helvetica", 16),
                           bg=bg)
    label_titre.pack(pady=10)

    # Add the adherent information
    # Image de profil en haut à droite
    img_profil = Image.open(adherent['img_profil'])
    img_profil = img_profil.resize((100, 100))
    img_profil_tk = ImageTk.PhotoImage(img_profil)
    label_img_profil = tk.Label(frame_principal, image=img_profil_tk, bg=bg)
    label_img_profil.pack(side="right", anchor="n", padx=10, pady=10)

    # Nom et prénom à gauche de l'image de profil
    label_nom_prenom = tk.Label(frame_principal, text=f"Nom: {adherent['nom']}\nPrénom: {adherent['prenom']}",
                                font=("Helvetica", 14), bg=bg)
    label_nom_prenom.pack(side="left", anchor="n", padx=10, pady=10)

    # Add the repas information
    # Table des items avec leurs quantités (centrée)
    cur.execute("SELECT item, quantite FROM plat WHERE plat_id=?", (id,))
    items_quantites = cur.fetchall()

    # Créer une Treeview (table) avec des colonnes "Élément" et "Quantité"
    table_items = ttk.Treeview(frame_principal, columns=("Element", "Quantite"), show="headings")
    table_items.heading("Element", text="Élément")
    table_items.heading("Quantite", text="Quantité")

    for item_quantite in items_quantites:
        table_items.insert("", "end", values=(item_quantite['item'], item_quantite['quantite']))

    table_items.pack(side="bottom", anchor="center", pady=20)

    # Image du plat centrée
    cur.execute("SELECT plat_id, plat_img FROM plat WHERE plat_id=?", (id,))
    plat = cur.fetchone()

    if plat:
        img_plat = Image.open(plat['plat_img'])
        img_plat = img_plat.resize((200, 200))
        img_plat_tk = ImageTk.PhotoImage(img_plat)
        label_img_plat = tk.Label(frame_principal, image=img_plat_tk, bg=bg)
        label_img_plat.pack(side="bottom", pady=20)

    conn.close()
    fenetre.update()

def read_rfid_data():
    while True:
        try:
            rfid_data = arduino_serial_port.readline().decode('utf-8').strip()
            afficher_adherent_et_repas(rfid_data, fenetre)
        except serial.SerialException as e:
            print(f"Erreur lecture du port série: {e}")


# Open the serial port
arduino_serial_port = serial.Serial('COM3')

# Start reading RFID data
read_rfid_data()

# Run the main loop
fenetre.mainloop()
##################################""
# CA MARCHE BIEN
#************
# @uthor: Nouamane SOUADI
# Creation Date	: 16/05/2024 on 20:51:47

# VERSION DESIGN
# import tkinter as tk
# from tkinter import ttk
# from PIL import Image, ImageTk
# import sqlite3
# import serial

# fenetre = tk.Tk()
# fenetre.geometry("800x750")
# bg = "#99D9EA"
# fenetre.configure(bg=bg)

# # Calculez les coordonnées x et y pour centrer la fenêtre sur l'écran
# largeur_ecran = fenetre.winfo_screenwidth()
# hauteur_ecran = fenetre.winfo_screenheight()
# x = (largeur_ecran - 800) // 2
# y = (hauteur_ecran - 800) // 2

# # Positionnez la fenêtre au centre de l'écran
# fenetre.geometry(f"800x800+{x}+{y}")

# def afficher_adherent_et_repas(id, fenetre):
#     try:
#         conn = sqlite3.connect('sqlite_TIPE.db')
#         conn.row_factory = sqlite3.Row
#         cur = conn.cursor()
#     except sqlite3.Error as e:
#         print(f"Erreur connexion à la base de donnée: {e}")
#         return 
    
#     cur.execute("SELECT * FROM adherent WHERE id=?", (id,))
#     adherent = cur.fetchone()

#     if adherent is None:
#         print(f"Aucun adhérent trouvé avec cet ID: '{id}'")
#         conn.close()
#         return

#     print(f"id détecté: '{id}'")

#     for widget in fenetre.winfo_children():
#         widget.destroy()

#     frame_principal = tk.Frame(fenetre, bg=bg)
#     frame_principal.pack(expand=True, fill="both")

#     # Image de profil en haut à droite
#     img_profil = Image.open(adherent['img_profil'])
#     img_profil = img_profil.resize((100, 100))
#     img_profil_tk = ImageTk.PhotoImage(img_profil)
#     label_img_profil = tk.Label(frame_principal, image=img_profil_tk)
#     label_img_profil.image = img_profil_tk
#     label_img_profil.pack(side="right", anchor="n", padx=10, pady=10)

#     # Nom et prénom à gauche de l'image de profil
#     label_nom_prenom = tk.Label(frame_principal, text=f"Nom: {adherent['nom']}\nPrénom: {adherent['prenom']}",
#                                 font=("Helvetica", 14), bg=bg)
#     label_nom_prenom.pack(side="left", anchor="n", padx=10, pady=10)

#     # Table des items avec leurs quantités (centrée)
#     cur.execute("SELECT item, quantite FROM plat WHERE plat_id=?", (id,))
#     items_quantites = cur.fetchall()

#     # Créer une Treeview (table) avec des colonnes "Élément" et "Quantité"
#     table_items = ttk.Treeview(frame_principal, columns=("Element", "Quantite"), show="headings")
#     table_items.heading("Element", text="Élément")
#     table_items.heading("Quantite", text="Quantité")

#     for item_quantite in items_quantites:
#         table_items.insert("", "end", values=(item_quantite['item'], item_quantite['quantite']))

#     table_items.pack(side="bottom", anchor="center", pady=20)

#     # Image du plat centrée
#     cur.execute("SELECT plat_id, plat_img FROM plat WHERE plat_id=?", (id,))
#     plat = cur.fetchone()

#     if plat:
#         img_plat = Image.open(plat['plat_img'])
#         img_plat = img_plat.resize((200, 200))
#         img_plat_tk = ImageTk.PhotoImage(img_plat)
#         label_img_plat = tk.Label(frame_principal, image=img_plat_tk)
#         label_img_plat.image = img_plat_tk
#         label_img_plat.pack(side="bottom", pady=20)

#     conn.close()
#     fenetre.update()

# arduino_serial_port = serial.Serial('COM3', 9600)

# def read_rfid_data():
#     while True:
#         try:
#             rfid_data = arduino_serial_port.readline().decode('utf-8').strip()
#             afficher_adherent_et_repas(rfid_data, fenetre)
#         except serial.SerialException as e:
#             print(f"Erreur lecture du port série: {e}")

# read_rfid_data()
# fenetre.mainloop()


###################################################
# #CA MARCHE BIEN
# import tkinter as tk
# from PIL import Image, ImageTk
# import sqlite3
# import serial
#
# fenetre = tk.Tk()  # Créez la fenêtre Tkinter
# # Créez la fenêtre Tkinter avec une taille fixe de 800x800 pixels
# fenetre.geometry("800x800")
# # Calculez les coordonnées x et y pour centrer la fenêtre sur l'écran
# largeur_ecran = fenetre.winfo_screenwidth()
# hauteur_ecran = fenetre.winfo_screenheight()
# x = (largeur_ecran - 800) // 2
# y = (hauteur_ecran - 800) // 2
#
# # Positionnez la fenêtre au centre de l'écran
# fenetre.geometry(f"800x800+{x}+{y}")
# def afficher_adherent_et_repas(id):
#     global fenetre
#
#     conn = sqlite3.connect('sqlite_new.db')
#     conn.row_factory = sqlite3.Row
#     cur = conn.cursor()
#
#     cur.execute("SELECT * FROM adherent WHERE id=?", (id,))
#     adherent = cur.fetchone()
#
#     if adherent is None:
#         print(f"Aucun adhérent trouvé avec cet ID: '{id}'")
#         conn.close()
#         return
#
#     print(f"id détecté: '{id}'")
#
#     for widget in fenetre.winfo_children():
#         widget.destroy()
#
#     label_nom_prenom = tk.Label(fenetre, text=f"Nom: {adherent['nom']}, Prénom: {adherent['prenom']}")
#     label_nom_prenom.pack()
#
#     img_profil = Image.open(adherent['img_profil'])
#     img_profil = img_profil.resize((100, 100))
#     img_profil_tk = ImageTk.PhotoImage(img_profil)
#     label_img_profil = tk.Label(fenetre, image=img_profil_tk)
#     label_img_profil.image = img_profil_tk
#     label_img_profil.pack()
#
#     # Sélectionnez les informations du plat
#     cur.execute("SELECT plat_id, plat_img FROM plat WHERE plat_id=?", (id,))
#     plat = cur.fetchone()
#
#     if plat:
#         # Charger et afficher l'image du plat (une seule fois)
#         img_plat = Image.open(plat['plat_img'])
#         img_plat = img_plat.resize((100, 100))
#         img_plat_tk = ImageTk.PhotoImage(img_plat)
#         label_img_plat = tk.Label(fenetre, image=img_plat_tk)
#         label_img_plat.image = img_plat_tk
#         label_img_plat.pack()
#
#         # Sélectionnez les items et quantités associés au plat
#         cur.execute("SELECT item, quantite FROM plat WHERE plat_id=?", (id,))
#         items_quantites = cur.fetchall()
#
#         for item_quantite in items_quantites:
#             # Ajoutez une étiquette avec le nom de l'item et la quantité
#             label_item_quantite = tk.Label(fenetre,
#                                            text=f"Item: {item_quantite['item']}, Quantité: {item_quantite['quantite']}")
#             label_item_quantite.pack()
#
#     conn.close()
#     fenetre.update()
#
# # Ouvrez le port série de l'Arduino
# arduino_serial_port = serial.Serial('COM3', 9600)
#
# def read_rfid_data():
#     while True:
#         rfid_data = arduino_serial_port.readline().decode('utf-8').strip()
#         afficher_adherent_et_repas(rfid_data)
#
# read_rfid_data()  # Lancez la lecture des données RFID
# fenetre.mainloop()