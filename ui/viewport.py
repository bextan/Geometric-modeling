import pyvista as pv

from PySide6.QtWidgets import QWidget, QVBoxLayout
from pyvistaqt import QtInteractor

import numpy as np

class Viewpoint(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.plotter = QtInteractor(self)
        self.plotter.set_background("#171A21")
        self.plotter.show_grid(
            color="#707070",
            xlabel="X",
            ylabel="Y",
            zlabel="Z",
        )
        self.plotter.add_axes(
            interactive=False,
            line_width=2,
            color="white"
        )

        self.plotter.enable_trackball_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotter)

    def setup_grid(self, mesh):
        bounds = mesh.bounds

        x_min, x_max = bounds[0], bounds[1]
        y_min, y_max = bounds[2], bounds[3]
        z_min, z_max = bounds[4], bounds[5]

        model_size = max(
            x_max - x_min,
            y_max - y_min,
            z_max - z_min
        )

        if model_size <= 0:
            return

        grid_spacing = model_size / 10

        # Grid around the world origin
        grid_size = grid_spacing * 50

        grid_lines = []

        for i in range(-50, 51):
            pos = i * grid_spacing

            # Lines parallel to X
            grid_lines.append(
                pv.Line(
                    (-grid_size, pos, 0),
                    (grid_size, pos, 0)
                )
            )

            # Lines parallel to Y
            grid_lines.append(
                pv.Line(
                    (pos, -grid_size, 0),
                    (pos, grid_size, 0)
                )
            )

        grid = pv.MultiBlock(grid_lines).combine()

        self.plotter.add_mesh(
            grid,
            color="#606060",
            line_width=1
        )

        print("Grid spacing:", grid_spacing)
        axis_length = grid_size

        self.plotter.add_mesh(
            pv.Line((-axis_length, 0, 0), (axis_length, 0, 0)),
            color="#D65A5A",
            line_width=3
        )

        self.plotter.add_mesh(
            pv.Line((0, -axis_length, 0), (0, axis_length, 0)),
            color="#75B86B",
            line_width=3
        )

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

        mesh = pv.PolyData(points, faces)
        self.plotter.clear()

        self.setup_grid(mesh)


        self.plotter.add_mesh(
            mesh,
            color="#B8C5D6",
            show_edges=True,
            edge_color="#252525",
            line_width=1,
            smooth_shading=False
        )
        self.plotter.reset_camera()
        self.plotter.render()