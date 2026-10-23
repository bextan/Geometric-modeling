import pyvista as pv

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu, QFileDialog
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from pyvistaqt import QtInteractor

import numpy as np
import math

class Viewport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.plotter = QtInteractor(self)
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
        layout.addWidget(self.plotter)
        self.setup_grid()

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

        subdivide_menu.addAction(loop)
        subdivide_menu.addAction(butterfly)
        menu.exec(event.globalPos())
        
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

    
    def show_mesh(self, file_mesh): 
        points = np.array([vertex.position for vertex in file_mesh.vertices])
        indices = []

        for face in file_mesh.faces:
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

    def set_open_file_callback(self, callback):
        self.open_file_callback = callback