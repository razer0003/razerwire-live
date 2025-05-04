from tkinter import Frame, Label, Entry, Button, filedialog, messagebox
import requests

class FileUploadWindow:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.frame = Frame(master)
        self.frame.pack(pady=20)

        self.label = Label(self.frame, text="Upload File:")
        self.label.pack()

        self.file_entry = Entry(self.frame, width=50)
        self.file_entry.pack(padx=5)

        self.browse_button = Button(self.frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.upload_button = Button(self.frame, text="Upload", command=self.upload_file)
        self.upload_button.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, 'end')
            self.file_entry.insert(0, file_path)

    def upload_file(self):
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload.")
            return

        url = "http://127.0.0.1:5000/upload"  # Adjust the URL as needed
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, files=files, data={'username': self.username})

        if response.status_code == 200:
            messagebox.showinfo("Success", "File uploaded successfully.")
        else:
            messagebox.showerror("Error", "Failed to upload file.")