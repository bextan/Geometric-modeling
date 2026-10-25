
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QAction

from ui.viewport import Viewport
from mesh_io.mesh_loader import MeshLoader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mesh Subdivision")
        self.resize(1200, 700)

        container = QWidget()
        self.setCentralWidget(container)

        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.viewport = Viewport()
        self.main_layout.addWidget(self.viewport, 1)

        self.mesh_loader = MeshLoader(self)

        self.viewport.set_open_file_callback(
            self.mesh_loader.open_file
        )

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.mesh_loader.open_file)
        file_menu.addAction(open_action)

        menubar.addSeparator()
        subdivide_menu = menubar.addMenu("Subdivide")
        loop = QAction("Loop", self)
        loop.triggered.connect(self.viewport.loop_subdivide)
        
        butterfly = QAction("Butterfly", self)
        butterfly.triggered.connect(self.viewport.butterfly_subdivide)

        subdivide_menu.addAction(loop)
        subdivide_menu.addAction(butterfly)
