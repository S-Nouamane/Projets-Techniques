import sqlite3
import pyserial
from PIL import Image, ImageTk
import tkinter as tk

# Connect to the RFID reader
ser = pyserial.Serial('COM3', 9600)

# Connect to the SQLite database
conn = sqlite3.connect('sqlite_TIPE.db')
c = conn.cursor()

# Function to read a tag from the RFID reader
def read_tag():
    while True:
        data = ser.read(10)
        if data:
            return data.decode('utf-8').strip()

# Function to get the user information from the database
def get_user_info(user_id):
    c.execute("SELECT * FROM adherent WHERE id=?", (user_id,))
    user = c.fetchone()
    return user

# Function to get the menu information for a user
def get_menu_info(user_id):
    c.execute("SELECT * FROM plats", )
    plats = c.fetchall()
    menu = {}
    for plat in plats:
        plat_id, plat_img, item, quantite = plat
        if plat_id not in menu:
            menu[plat_id] = {'plat_img': plat_img, 'items': {}}
        menu[plat_id]['items'][item] = quantite
    return menu

# Function to display the user information
def display_user_info(user):
    profile_img.config(image=user_photo)
    name_label.config(text=f'{user[1]} {user[2]}')

# Function to display the menu information
def display_menu_info(menu):
    menu_frame.delete('all')
    for plat_id, info in menu.items():
        plat_img = ImageTk.PhotoImage(Image.open(info['plat_img']))
        menu_img = tk.Label(menu_frame, image=plat_img)
        menu_img.image = plat_img
        menu_img.grid(row=menu_row, column=0, padx=10, pady=10)

        items_frame = tk.Frame(menu_frame)
        items_frame.grid(row=menu_row, column=1, padx=10, pady=10)

        for item, quantite in info['items'].items():
            tk.Label(items_frame, text=f'{item}: {quantite}', font=('Arial', 12), fg='#333').grid(padx=10, pady=10)

        menu_row += 1

# Create the Tkinter interface
window = tk.Tk()
window.title('RFID Menu')
window.geometry('800x600')
window.configure(bg='#f0f0f0')

profile_frame = tk.Frame(window, bg='#fff')
profile_frame.grid(row=0, column=0, padx=10, pady=10)

profile_img = tk.Label(profile_frame, bg='#fff')
profile_img.grid(row=0, column=0, padx=10, pady=10)

name_label = tk.Label(profile_frame, text='', font=('Arial', 20), fg='#333')
name_label.grid(row=1, column=0, padx=10, pady=10)

menu_frame = tk.Frame(window, bg='#fff')
menu_frame.grid(row=1, column=0, padx=10, pady=10)

menu_row = 0

# Main loop
while True:
    # Read a tag from the RFID reader
    user_id = read_tag()
    if user_id:
        print(f'User ID: {user_id}')

        # Get the user information from the database
        user = get_user_info(user_id)
        if user:
            print(f'Name: {user[1]} {user[2]}')
            user_photo = ImageTk.PhotoImage(Image.open(user[3]))
            display_user_info(user)

            # Get the menu information for the user
            menu = get_menu_info(user_id)
            if menu:
                print('Menu:')
                display_menu_info(menu)

    else:
        print('No tag detected')

# Close the database connection
conn.close()

window.mainloop()