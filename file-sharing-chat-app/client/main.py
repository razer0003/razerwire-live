from tkinter import Tk
from client.gui.login import LoginWindow

def main():
    root = Tk()
    root.title("File Sharing and Chat Application")
    root.geometry("400x300")
    
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()