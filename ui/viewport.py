import pyvista as pv

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
    QLabel,
    )

from PySide6.QtGui import QAction
from pyvistaqt import QtInteractor
from algorithms.loop import LoopSubdivision
from algorithms.butterfly import ButterflySubdivision
from PySide6.QtCore import QThread
from ui.task_worker import TaskWorker
from ui.loading_overlay import LoadingOverlay
import numpy as np
import math
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

class Viewport(QWidget):
    mesh_stats_updated = Signal(int, int, int, int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subdivide_shortcut = QShortcut(
            QKeySequence("R"),
            self
        )
        self.subdivide_shortcut.activated.connect(self.subdivide_again)

        self.current_scheme = None
        self.subdivision_level = 0
        self.task_thread = None
        self.task_worker = None

        self.plotter = QtInteractor(self)
        self.plotter.enable_lightkit()
        self.plotter.enable_ssao(
            radius=0.5,
            bias=0.01,
            kernel_size=128
        )

        self.plotter.enable_anti_aliasing("fxaa")

        self.plotter.set_background("#171A21")
        self.plotter.add_axes(
            interactive=False,
            line_width=2,
            color="white"
        )


        self.plotter.enable_trackball_style()


        self.current_grid_spacing = None
        self.grid_actors = []

        self.plotter.iren.add_observer(
            "MouseWheelForwardEvent",
            self.update_grid
        )

        self.plotter.iren.add_observer(
            "MouseWheelBackwardEvent",
            self.update_grid
        )
        self.plotter.iren.add_observer(
            "KeyPressEvent",
            self.update_mesh_style
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
    
        layout.addWidget(self.plotter)

        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setGeometry(self.rect())
        self.loading_overlay.hide()

        self.setup_grid()

    def run_task(self, task, *args, on_finished, **kwargs):
        if self.task_thread is not None:
            return

        self.loading_overlay.set_progress(0)
        self.loading_overlay.set_message("Starting...")
        self.loading_overlay.show()
        self.loading_overlay.raise_()

        self.task_thread = QThread(self)
        self.task_worker = TaskWorker(task, *args, **kwargs)
        self.task_worker.moveToThread(self.task_thread)

        self.task_thread.started.connect(self.task_worker.run)

        self.task_worker.progress.connect(self.on_task_progress)
        self.task_worker.finished.connect(on_finished)
        self.task_worker.error.connect(self.on_task_error)

        self.task_worker.finished.connect(self.task_thread.quit)
        self.task_worker.error.connect(self.task_thread.quit)

        self.task_thread.finished.connect(self.loading_overlay.hide)
        self.task_thread.finished.connect(self.cleanup_task)
        self.task_thread.finished.connect(self.task_worker.deleteLater)
        self.task_thread.finished.connect(self.task_thread.deleteLater)

        self.task_thread.start()


    def cleanup_task(self):
        self.task_worker = None
        self.task_thread = None

    def on_task_error(self, message):
        print(f"Task failed: {message}")


        
    def update_mesh_style(self, caller, event):
        key = caller.GetKeySym()

        if not hasattr(self, "mesh_actor"):
            return

        if key == "z":
            self.mesh_actor.GetProperty().SetRepresentationToWireframe()
        elif key == "x":
            self.mesh_actor.GetProperty().SetRepresentationToSurface()

        self.plotter.render()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        file_menu = menu.addMenu("File")
        open_action = QAction("Open...", self)

        open_action.triggered.connect(
            lambda: self.open_file_callback()
        )

        file_menu.addAction(open_action)
        menu.addSeparator()

        subdivide_menu = menu.addMenu("Subdivide")
        loop = QAction("Loop", self)
        butterfly = QAction("Butterfly", self)

        loop.triggered.connect(self.loop_subdivide)
        butterfly.triggered.connect(self.butterfly_subdivide)
        subdivide_menu.addAction(loop)
        subdivide_menu.addAction(butterfly)
        menu.exec(event.globalPos())

    def on_task_progress(self, value, message):
        self.loading_overlay.set_progress(value)
        self.loading_overlay.set_message(message)
    def loop_subdivide(self):
        self.current_scheme = "Loop"
        self.subdivide_again()


    def butterfly_subdivide(self):
        self.current_scheme = "Butterfly"
        self.subdivide_again()


    def subdivide_again(self):
        if not hasattr(self, "current_mesh"):
            return

        if self.current_scheme is None:
            return

        if self.task_thread is not None:
            return

        if self.current_scheme == "Loop":
            algorithm = LoopSubdivision(self.current_mesh)
        elif self.current_scheme == "Butterfly":
            algorithm = ButterflySubdivision(self.current_mesh)
        else:
            return

        self.run_task(
            algorithm.subdivide,
            on_finished=self.on_subdivision_finished
        )

    def on_subdivision_finished(self, mesh):
        self.subdivision_level += 1
        self.add_mesh(mesh, reset_level=False)
        
    def setup_grid(self, mesh=None):
        
        if mesh is not None:
            bounds = mesh.bounds

            model_size = max(
                bounds[1] - bounds[0],
                bounds[3] - bounds[2],
                bounds[5] - bounds[4]
            )

            if not np.isfinite(model_size) or model_size <= 0:
                return

            spacing = model_size / 10
        else:
            spacing = 1.0

        self.setup_grid_with_spacing(spacing)


    def setup_grid_with_spacing(self, spacing):
        self.clear_grid()

        grid_spacing = spacing
        camera_position = self.plotter.camera.position
        focal_point = self.plotter.camera.focal_point

        camera_distance = np.linalg.norm(
            np.array(camera_position) - np.array(focal_point)
        )

        line_count = int(np.clip(camera_distance / 5, 20, 50))
        grid_size = spacing * line_count



        minor_lines = []
        major_lines = []

        for i in range(-line_count, line_count + 1):
            if i == 0:
                continue

            pos = i * grid_spacing
            target = major_lines if i % 5 == 0 else minor_lines

            target.append(
                pv.Line((-grid_size, pos, 0), (grid_size, pos, 0))
            )
            target.append(
                pv.Line((pos, -grid_size, 0), (pos, grid_size, 0))
            )

        self.plotter.set_background("#282828")

        if minor_lines:
            actor = self.plotter.add_mesh(
                pv.MultiBlock(minor_lines).combine(),
                color="#414141",
                line_width=1,
                reset_camera=False
            )
            self.grid_actors.append(actor)

        if major_lines:
            actor = self.plotter.add_mesh(
                pv.MultiBlock(major_lines).combine(),
                color="#606060",
                line_width=1.5,
                reset_camera=False
            )
            self.grid_actors.append(actor)

        for line, color in [
            (pv.Line((-grid_size, 0, 0), (grid_size, 0, 0)), "#D65A5A"),
            (pv.Line((0, -grid_size, 0), (0, grid_size, 0)), "#75B86B"),
            (pv.Line((0, 0, -grid_size), (0, 0, grid_size)), "#6585D0"),
        ]:
            actor = self.plotter.add_mesh(
                line,
                color=color,
                line_width=2,
                reset_camera=False
            )
            self.grid_actors.append(actor)

        self.current_grid_spacing = grid_spacing

    def get_grid_spacing(self, camera_distance):
        raw_spacing = camera_distance / 15

        if raw_spacing <= 0:
            return 1.0

        exponent = math.floor(math.log10(raw_spacing))
        magnitude = 10 ** exponent
        fraction = raw_spacing / magnitude

        if fraction < 2:
            nice_number = 1
        elif fraction < 5:
            nice_number = 2
        else:
            nice_number = 5

        return nice_number * magnitude

    def clear_grid(self):
        for actor in self.grid_actors:
            self.plotter.remove_actor(actor, render=False)

        self.grid_actors.clear()

    def update_grid(self, *args):
        camera_position = self.plotter.camera.position
        focal_point = self.plotter.camera.focal_point

        camera_distance = np.linalg.norm(
            np.array(camera_position) - np.array(focal_point)
        )

        new_spacing = self.get_grid_spacing(camera_distance)

        if new_spacing == self.current_grid_spacing:
            return

        self.setup_grid_with_spacing(new_spacing)
        self.plotter.render()

    
    def add_mesh(self, input_mesh, reset_level=True):
        self.current_mesh = input_mesh

        if reset_level:
            self.subdivision_level = 0
            self.current_scheme = None

        self.update_mesh_stats()
        self.current_mesh = input_mesh 
        points = np.array([vertex.position for vertex in input_mesh.vertices])
        indices = []

        for face in input_mesh.faces:
            start = face.half_edge
            edge = start
            face_vertices = []

            while True:
                face_vertices.append(edge.origin.index)
                edge = edge.next

                if edge == start:
                    indices.append(len(face_vertices))
                    for vertex in face_vertices:
                        indices.append(vertex)
                    break

        faces = np.array(indices)

        self.mesh = pv.PolyData(points, faces)

        self.plotter.clear()
        self.grid_actors.clear()
        self.setup_grid(self.mesh)

        self.mesh_actor = self.plotter.add_mesh(
            self.mesh,
            color="#B8C5D6",
            show_edges=True,
            edge_color="#353535",
            line_width=1,
            smooth_shading=False,
            ambient=0.2,
            diffuse=0.8,
            specular=0.15,
            reset_camera=False
        )

        self.plotter.reset_camera()
        self.plotter.render()

    def update_mesh_stats(self):
        if self.current_mesh is None:
            self.mesh_stats_updated.emit(0, 0, 0, 0)
            return

        vertices = len(self.current_mesh.vertices)
        edges = len(self.current_mesh.get_unique_edges())
        faces = len(self.current_mesh.faces)

        self.mesh_stats_updated.emit(
            vertices,
            edges,
            faces,
            self.subdivision_level,
        )
    def set_open_file_callback(self, callback):
        
        self.open_file_callback = callback