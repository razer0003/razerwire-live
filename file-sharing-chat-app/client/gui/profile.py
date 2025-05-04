from tkinter import Tk, Label, Entry, Button, messagebox
import requests

class ProfileWindow:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("Profile Management")
        self.master.geometry("400x300")

        self.label_username = Label(master, text="Username:")
        self.label_username.pack(pady=10)

        self.entry_username = Entry(master)
        self.entry_username.pack(pady=10)
        self.entry_username.insert(0, username)
        self.entry_username.config(state='readonly')

        self.label_bio = Label(master, text="Bio:")
        self.label_bio.pack(pady=10)

        self.entry_bio = Entry(master)
        self.entry_bio.pack(pady=10)

        self.button_save = Button(master, text="Save Changes", command=self.save_profile)
        self.button_save.pack(pady=20)

        self.load_profile()

    def load_profile(self):
        response = requests.get(f'http://localhost:5000/api/profile/{self.username}')
        if response.status_code == 200:
            profile_data = response.json()
            self.entry_bio.delete(0, 'end')
            self.entry_bio.insert(0, profile_data.get('bio', ''))
        else:
            messagebox.showerror("Error", "Failed to load profile data.")

    def save_profile(self):
        bio = self.entry_bio.get()
        response = requests.put(f'http://localhost:5000/api/profile/{self.username}', json={'bio': bio})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Profile updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to update profile.")