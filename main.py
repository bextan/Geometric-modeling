from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

import sys


def startWindow():
    app = QApplication(sys.argv)
    
    mainWindow = MainWindow()
    mainWindow.show()

    app.exec()


if __name__ == "__main__":
    startWindow()