import trimesh
from mesh.mesh import Mesh
from mesh.vertex import Vertex
from mesh.half_edge import HalfEdge
from mesh.face import Face

from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QLabel, QWidget, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal

from pathlib import Path

class MeshLoader(QThread):

    progress = Signal(int, str)
    loaded = Signal(object)
    failed = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.loading_overlay = LoadingOverlay(parent.viewport)
        self.loading_overlay.setGeometry(parent.viewport.rect())

        self.loaded.connect(self.on_mesh_loaded)
        self.failed.connect(self.on_mesh_error)
        self.progress.connect(self.loading_overlay.set_progress)
        self.progress.connect(self.update_loading_message)

    def run(self):
        try:
            mesh = self.load_mesh()
            self.loaded.emit(mesh)
        except Exception as e:
            self.failed.emit(str(e))
    def open_file(self, checked=False):
        parent = self.parent_window

        self.file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Choose a mesh file",
            "",
            "Mesh Files (*.stl *.obj);;All Files (*)"
        )

        if not self.file_path:
            return

        self.loading_overlay.set_progress(0)
        self.loading_overlay.set_message("Loading mesh...")
        self.loading_overlay.setGeometry(parent.viewport.rect())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

        self.start()


    
    def load_mesh(self):
        self.progress.emit(5, "Reading file...")
        path = Path(self.file_path)

        # if path.suffix.lower() not in (".stl", ".obj"):
        #     raise ValueError("Only STL and OBJ files are supported")
        
        file_mesh = trimesh.load(path, force="mesh", process=True)
        if not isinstance(file_mesh, trimesh.Trimesh):
            raise TypeError("The file did not produce a triangular mesh")

        custom_mesh = Mesh()

        self.progress.emit(25, "Building vertices...")
        custom_mesh.build_vertices(file_mesh.vertices)

        self.progress.emit(45, "Building faces...")
        custom_mesh.build_faces_and_halfedges(file_mesh.faces)

        self.progress.emit(70, "Connecting half-edges...")
        custom_mesh.connect_half_edges()
        self.progress.emit(95, "Finalizing mesh...")
        return custom_mesh

    def update_loading_message(self, value, message):
        self.loading_overlay.set_message(message)
        self.loading_overlay.set_progress(value)
    def on_mesh_loaded(self, file_mesh):
        self.loading_overlay.set_progress(100)
        self.loading_overlay.set_message("Mesh loaded!")
        self.loading_overlay.hide()
        self.parent_window.viewport.add_mesh(file_mesh)
    
    def on_mesh_error(self, error):
        self.loading_overlay.hide()

        print("Failed to load mesh:", error)
    

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cover the viewport with a transparent dark overlay
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(0, 0, 0, 130);
            }
        """)

        # Center the loading window
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Modal-like panel
        self.panel = QWidget()
        self.panel.setFixedWidth(360)
        self.panel.setStyleSheet("""
            QWidget {
                background-color: #20252B;
                border: 1px solid #3A424C;
                border-radius: 12px;
            }
        """)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(24, 24, 24, 24)
        panel_layout.setSpacing(18)

        # Loading label
        self.label = QLabel("Loading mesh...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #E6EAF0;
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: 500;
            }
        """)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #343B45;
                border: none;
                border-radius: 6px;
                text-align: center;
                color: white;
            }

            QProgressBar::chunk {
                background-color: #3984F5;
                border-radius: 6px;
            }
        """)

        panel_layout.addWidget(self.label)
        panel_layout.addWidget(self.progress_bar)

        outer_layout.addWidget(self.panel)

        self.hide()

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def set_message(self, message):
        self.label.setText(message)