from tkinter import Tk, Text, Scrollbar, Entry, Button, END, Frame, Label
import requests

class ChatApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("Chat Application")
        self.master.geometry("400x500")

        self.frame = Frame(self.master)
        self.frame.pack(pady=10)

        self.chat_log = Text(self.frame, width=50, height=20, state='disabled')
        self.chat_log.pack(side='left')

        self.scrollbar = Scrollbar(self.frame, command=self.chat_log.yview)
        self.scrollbar.pack(side='right', fill='y')

        self.chat_log.config(yscrollcommand=self.scrollbar.set)

        self.message_entry = Entry(self.master, width=40)
        self.message_entry.pack(pady=10)

        self.send_button = Button(self.master, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.load_chat()

    def load_chat(self):
        response = requests.get(f'http://localhost:5000/chat/{self.username}')
        if response.status_code == 200:
            messages = response.json()
            self.chat_log.config(state='normal')
            for message in messages:
                self.chat_log.insert(END, f"{message['username']}: {message['message']}\n")
            self.chat_log.config(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            payload = {'username': self.username, 'message': message}
            response = requests.post('http://localhost:5000/chat/send', json=payload)
            if response.status_code == 200:
                self.message_entry.delete(0, END)
                self.load_chat()

if __name__ == "__main__":
    root = Tk()
    username = "User"  # Replace with actual username from login
    app = ChatApp(root, username)
    root.mainloop()