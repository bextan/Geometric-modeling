from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
)

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesh Subdivision")
        self.resize(1200, 700)

