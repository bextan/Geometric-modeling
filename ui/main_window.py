from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog
)

from PySide6.QtCore import Qt

from mesh_struct.mesh_converter import load_mesh

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self):
        self.setWindowTitle("Mesh Subdivision")
        self.resize(1200, 700)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loadFileButton = QPushButton("Load file")
        loadFileButton.clicked.connect(self.load_file)
        loadFileButton.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        loadFileButton.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(loadFileButton)
        
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a mesh file",
            "",
            "Mesh Files (*.stl *.obj);;All Files (*)"
        )

        custom_mesh = load_mesh(file_path)
        
        print("Vertices:", len(custom_mesh.vertices))
        print("Half-edges:", len(custom_mesh.half_edges))
        print("Faces:", len(custom_mesh.faces))

