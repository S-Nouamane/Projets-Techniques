#************
# @uthor: Nouamane SOUADI
# Creation Date	: 16/05/2024 on 20:39:28

import sqlite3
import tkinter as tk
import serial
from PIL import Image, ImageTk

conn = sqlite3.connect('sqlite_TIPE.db')
c = conn.cursor()

def read_rfid():
    ser = serial.Serial("COM3", 9600)
    id = ser.readline().decode('utf-8').strip()
    ser.close()
    return id

def display_info():
    id = read_rfid()
    c.execute("SELECT * FROM adherent WHERE id =?", (id,))
    adherent = c.fetchone()
    if adherent is None: # vérifier l'utilsateur
        print("Badge non trouvé")
        return
    c.execute("SELECT * FROM plat WHERE id =?", (id,))
    plat = c.fetchone()
    if plat is None: # vérifier l'existence d'un plat
        print("Plat non trouvé")
        return

    # Create a Tkinter frame to display the adherent's information
    adherent_frame = tk.Frame(root, bg="white")
    adherent_frame.pack(fill="x")

    # Display the adherent's name and surname
    name_label = tk.Label(adherent_frame, text=f"Name: {adherent[1]} {adherent[2]}", font=("Arial", 16))
    name_label.pack()

    # Display the adherent's profile image
    profile_image = Image.open(adherent[3])
    profile_image = ImageTk.PhotoImage(profile_image)
    profile_image_label = tk.Label(adherent_frame, image=profile_image)
    profile_image_label.pack()

    # Create a Tkinter frame to display the plat's information
    plat_frame = tk.Frame(root, bg="white")
    plat_frame.pack(fill="x")

    # Display the plat's image
    plat_image = Image.open(plat[2])
    plat_image = ImageTk.PhotoImage(plat_image)
    plat_image_label = tk.Label(plat_frame, image=plat_image)
    plat_image_label.pack()

    # Display the plat's items and quantities
    items_label = tk.Label(plat_frame, text="Items:", font=("Arial", 14))
    items_label.pack()
    for item, quantity in zip(plat[3:], plat[4:]):
        item_label = tk.Label(plat_frame, text=f"{item}: {quantity}", font=("Arial", 12))
        item_label.pack()

    # Update the Tkinter window
    root.update_idletasks()

root = tk.Tk()
# Ajoutez des éléments comme des labels, des entrées de texte, des images, etc.
#...

display_info()
root.mainloop()