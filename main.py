import traceback
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import JanelaDownloaderYouTube
from tkinter import messagebox

def principal():
    try:
        app = QApplication([])
        window = JanelaDownloaderYouTube()
        window.show()
        app.exec_()
    except Exception as e:
        messagebox.showerror("Erro", traceback.format_exc())

if __name__ == "__main__":
    principal()