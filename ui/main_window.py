from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

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

        # Top information panel
        self.info_bar = QWidget()
        self.info_layout = QHBoxLayout(self.info_bar)
        self.info_layout.setContentsMargins(12, 6, 12, 6)
        self.info_layout.setSpacing(24)

        self.vertices_label = QLabel("Vertices: 0")
        self.edges_label = QLabel("Edges: 0")
        self.faces_label = QLabel("Faces: 0")
        self.level_label = QLabel("Subdivision: 0")

        for label in (
            self.vertices_label,
            self.edges_label,
            self.faces_label,
            self.level_label,
        ):
            label.setStyleSheet(
                "color: #E6E6E6; font-size: 13px;"
            )
            self.info_layout.addWidget(label)

        self.info_layout.addStretch()


        self.info_bar.setStyleSheet(
            "background-color: #282828;"
        )

        self.main_layout.addWidget(self.info_bar)

        # 3D viewport
        self.viewport = Viewport()
        self.main_layout.addWidget(self.viewport, 1)

        # Mesh loading
        self.mesh_loader = MeshLoader(self)

        self.viewport.set_open_file_callback(
            self.mesh_loader.open_file
        )

        # Connect viewport statistics to the information panel
        self.viewport.mesh_stats_updated.connect(
            self.update_mesh_stats
        )

        # Menu bar
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        open_action = QAction("Open...", self)
        open_action.triggered.connect(
            self.mesh_loader.open_file
        )
        file_menu.addAction(open_action)

        subdivide_menu = menubar.addMenu("Subdivide")

        loop = QAction("Loop", self)
        loop.triggered.connect(
            self.viewport.loop_subdivide
        )

        butterfly = QAction("Butterfly", self)
        butterfly.triggered.connect(
            self.viewport.butterfly_subdivide
        )

        subdivide_menu.addAction(loop)
        subdivide_menu.addAction(butterfly)

    def update_mesh_stats(
        self, vertices, edges, faces, subdivision_level
    ):
        self.vertices_label.setText(f"Vertices: {vertices}")
        self.edges_label.setText(f"Edges: {edges}")
        self.faces_label.setText(f"Faces: {faces}")
        self.level_label.setText(
            f"Subdivision: {subdivision_level}"
        )

    def viewport_subdivide_again(self):
        self.viewport.subdivide_again()

