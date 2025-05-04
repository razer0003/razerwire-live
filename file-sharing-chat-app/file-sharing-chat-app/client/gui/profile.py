from tkinter import Toplevel, Label, Entry, Button, messagebox
import requests

class ProfileWindow:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("Profile Management")
        self.master.geometry("300x200")

        self.label_username = Label(master, text="Username:")
        self.label_username.pack(pady=5)

        self.entry_username = Entry(master)
        self.entry_username.pack(pady=5)
        self.entry_username.insert(0, username)
        self.entry_username.config(state='readonly')

        self.label_email = Label(master, text="Email:")
        self.label_email.pack(pady=5)

        self.entry_email = Entry(master)
        self.entry_email.pack(pady=5)

        self.button_save = Button(master, text="Save Changes", command=self.save_changes)
        self.button_save.pack(pady=10)

        self.load_profile()

    def load_profile(self):
        response = requests.get(f'http://localhost:5000/api/profile/{self.username}')
        if response.status_code == 200:
            profile_data = response.json()
            self.entry_email.insert(0, profile_data.get('email', ''))
        else:
            messagebox.showerror("Error", "Failed to load profile data.")

    def save_changes(self):
        email = self.entry_email.get()
        response = requests.put(f'http://localhost:5000/api/profile/{self.username}', json={'email': email})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Profile updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to update profile.")