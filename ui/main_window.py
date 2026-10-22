from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal

from mesh_struct.mesh_converter import load_mesh
from PySide6.QtGui import QAction

from ui.viewport import Viewpoint

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self):
        self.setWindowTitle("Mesh Subdivision")
        self.resize(1200, 700)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        container = QWidget()
        self.setCentralWidget(container)

        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.viewport = Viewpoint(self)
        self.main_layout.addWidget(self.viewport, 1)

        self.loading_overlay = LoadingOverlay(self.viewport)
        self.loading_overlay.setGeometry(self.viewport.rect())
        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a mesh file",
            "",
            "Mesh Files (*.stl *.obj);;All Files (*)"
        )

        if not file_path:
            return

        self.loading_overlay.setGeometry(self.viewport.rect())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

        self.loader = MeshLoader(file_path)
        self.loader.loaded.connect(self.on_mesh_loaded)
        self.loader.failed.connect(self.on_mesh_error)
        self.loader.start()


    def on_mesh_loaded(self, file_mesh):
        self.loading_overlay.hide()

        self.viewport.show_mesh(file_mesh)
  
        
        print("Vertices:", len(file_mesh.vertices))
        print("Half-edges:", len(file_mesh.half_edges))
        print("Faces:", len(file_mesh.faces))



    def on_mesh_error(self, error):
        self.loading_overlay.hide()

        print("Failed to load mesh:", error)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150);
            }
            QLabel {
                color: white;
                font-size: 18px;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(self)

        label = QLabel("Loading mesh...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        self.hide()
class MeshLoader(QThread):
    loaded = Signal(object)
    failed = Signal(str)

    def __init__(self, file_path):
        
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            mesh = load_mesh(self.file_path)
            self.loaded.emit(mesh)
        except Exception as e:
            self.failed.emit(str(e))