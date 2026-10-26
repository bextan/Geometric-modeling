import trimesh
from mesh.mesh import Mesh

from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QThread, Signal

from pathlib import Path

from ui.loading_overlay import LoadingOverlay
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
    

