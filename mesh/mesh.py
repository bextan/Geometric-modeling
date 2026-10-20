

class Mesh:

    def __init__(self, vertices, half_edges, faces):
        self.vertices = vertices
        self.half_edges = half_edges
        self.faces = faces


    def __repr__(self):
            return (
                f"Mesh(vertices={len(self.vertices)}, "
                f"half_edges={len(self.half_edges)}, "
                f"faces={len(self.faces)})"
            )