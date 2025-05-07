import sys
import traceback
from PyQt5.QtWidgets import QApplication
from GUI import YouTubeDownloaderWindow
from tkinter import messagebox

def main():
    try:
        app = QApplication([])
        window = YouTubeDownloaderWindow()
        window.show()
        app.exec_()
    except Exception as e:
        messagebox.showerror("Erro", traceback.format_exc())

if __name__ == "__main__":
    main()