from tkinter import Tk, Label, Button, filedialog, messagebox
import requests

class FileUpload:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("File Upload")
        self.master.geometry("300x200")

        self.label = Label(master, text="Select a file to upload:")
        self.label.pack(pady=10)

        self.upload_button = Button(master, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=20)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.send_file_to_server(file_path)

    def send_file_to_server(self, file_path):
        url = "http://localhost:5000/upload"  # Adjust the URL as needed
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, files=files, data={'username': self.username})

        if response.status_code == 200:
            messagebox.showinfo("Success", "File uploaded successfully.")
        else:
            messagebox.showerror("Error", "Failed to upload file.")

if __name__ == "__main__":
    root = Tk()
    app = FileUpload(root, "test_user")  # Replace "test_user" with actual username
    root.mainloop()