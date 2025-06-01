from tkinter import Tk, Label, Entry, Button, messagebox
import requests
#test
class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Login")

        self.label_username = Label(master, text="Username:")
        self.label_username.pack()

        self.entry_username = Entry(master)
        self.entry_username.pack()

        self.label_password = Label(master, text="Password:")
        self.label_password.pack()

        self.entry_password = Entry(master, show='*')
        self.entry_password.pack()

        self.button_login = Button(master, text="Login", command=self.login)
        self.button_login.pack()

        self.button_register = Button(master, text="Register", command=self.register)
        self.button_register.pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        response = requests.post("http://localhost:5000/api/login", json={"username": username, "password": password})

        if response.status_code == 200:
            messagebox.showinfo("Success", "Logged in successfully!")
            # Proceed to the main application
        else:
            messagebox.showerror("Error", response.json().get("message", "Login failed."))

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        response = requests.post("http://localhost:5000/api/register", json={"username": username, "password": password})

        if response.status_code == 201:
            messagebox.showinfo("Success", "Registered successfully! You can now log in.")
        else:
            messagebox.showerror("Error", response.json().get("message", "Registration failed."))

if __name__ == "__main__":
    root = Tk()
    login_window = LoginWindow(root)
    root.mainloop()