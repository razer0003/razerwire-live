from tkinter import Frame, Label, Text, Entry, Button, Scrollbar, END, VERTICAL, RIGHT, Y
import requests

class ChatWindow:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("Chat")
        self.master.geometry("400x400")

        self.chat_frame = Frame(self.master)
        self.chat_frame.pack(pady=10)

        self.chat_log = Text(self.chat_frame, height=15, width=50, state='disabled')
        self.chat_log.pack(side='left', fill='both', expand=True)

        self.scrollbar = Scrollbar(self.chat_frame, orient=VERTICAL, command=self.chat_log.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.chat_log.config(yscrollcommand=self.scrollbar.set)

        self.message_entry = Entry(self.master, width=40)
        self.message_entry.pack(pady=10)

        self.send_button = Button(self.master, text="Send", command=self.send_message)
        self.send_button.pack()

        self.load_chat_history()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            response = requests.post('http://127.0.0.1:5000/chat/send', json={'username': self.username, 'message': message})
            if response.status_code == 200:
                self.message_entry.delete(0, END)
                self.load_chat_history()

    def load_chat_history(self):
        response = requests.get('http://127.0.0.1:5000/chat/history', params={'username': self.username})
        if response.status_code == 200:
            messages = response.json()
            self.chat_log.config(state='normal')
            self.chat_log.delete(1.0, END)
            for msg in messages:
                self.chat_log.insert(END, f"{msg['username']}: {msg['message']}\n")
            self.chat_log.config(state='disabled')
            self.chat_log.see(END)  # Scroll to the bottom
