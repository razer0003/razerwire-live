from tkinter import Toplevel, Label, Entry, Button, messagebox
import requests

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        
        self.label_username = Label(master, text="Username:")
        self.label_username.pack(pady=5)
        
        self.entry_username = Entry(master)
        self.entry_username.pack(pady=5)
        
        self.label_password = Label(master, text="Password:")
        self.label_password.pack(pady=5)
        
        self.entry_password = Entry(master, show='*')
        self.entry_password.pack(pady=5)
        
        self.button_login = Button(master, text="Login", command=self.login)
        self.button_login.pack(pady=20)
        
        self.button_create_account = Button(master, text="Create Account", command=self.create_account)
        self.button_create_account.pack(pady=5)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        response = requests.post("http://127.0.0.1:5000/login", json={"username": username, "password": password})
        
        if response.status_code == 200:
            messagebox.showinfo("Login Successful", "Welcome!")
            self.master.destroy()  # Close the login window
            # Here you would typically open the main application window
        else:
            messagebox.showerror("Login Failed", response.json().get("message", "Invalid credentials"))

    def create_account(self):
        # Logic to open the account creation window
        pass  # This should be implemented in a separate method or class