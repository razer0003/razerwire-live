from tkinter import Tk, Frame, Label, Button, Listbox, Scrollbar, Entry, messagebox
import requests
import json

class FileSharingApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("File Sharing and Chat Application")
        self.master.geometry("600x800")

        self.create_widgets()
        self.populate_user_list()

    def create_widgets(self):
        # Welcome label
        label_welcome = Label(self.master, text=f"Welcome, {self.username}!", font=("Arial", 16))
        label_welcome.pack(pady=10)

        # Search bar for users
        search_frame = Frame(self.master)
        search_frame.pack(pady=10)

        search_label = Label(search_frame, text="Search User:")
        search_label.pack(side='left', padx=5)

        self.search_entry = Entry(search_frame)
        self.search_entry.pack(side='left', padx=5)

        search_button = Button(search_frame, text="Search", command=self.search_user)
        search_button.pack(side='left', padx=5)

        # Scrollable list of users
        self.user_list_frame = Frame(self.master)
        self.user_list_frame.pack(pady=10, fill='both', expand=True)

        self.user_listbox = Listbox(self.user_list_frame, height=15, width=50)
        self.user_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(self.user_list_frame, orient='vertical', command=self.user_listbox.yview)
        scrollbar.pack(side='right', fill='y')

        self.user_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons for functionality
        button_upload = Button(self.master, text="Upload File", command=self.upload_file)
        button_upload.pack(pady=10)

        button_chat = Button(self.master, text="Chat", command=self.open_chat)
        button_chat.pack(pady=10)

        button_logout = Button(self.master, text="Logout", command=self.logout)
        button_logout.pack(pady=10)

    def populate_user_list(self):
        response = requests.get("http://127.0.0.1:5000/api/users")  # Adjust the endpoint as needed
        if response.status_code == 200:
            user_data = response.json()
            self.user_listbox.delete(0, 'end')
            for user in user_data:
                self.user_listbox.insert('end', user)
        else:
            messagebox.showerror("Error", "Failed to retrieve user list.")

    def search_user(self):
        query = self.search_entry.get().lower()
        self.user_listbox.delete(0, 'end')
        response = requests.get(f"http://127.0.0.1:5000/api/users/search?query={query}")
        if response.status_code == 200:
            user_data = response.json()
            for user in user_data:
                self.user_listbox.insert('end', user)
        else:
            messagebox.showerror("Error", "Failed to search users.")

    def upload_file(self):
        # Implement file upload functionality
        pass

    def open_chat(self):
        # Implement chat functionality
        pass

    def logout(self):
        # Implement logout functionality
        pass

def show_main_screen(username):
    root = Tk()
    app = FileSharingApp(root, username)
    root.mainloop()