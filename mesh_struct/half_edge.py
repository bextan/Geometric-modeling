from mesh_struct.face import Face

class HalfEdge:
    def __init__(self, origin):
        self.origin = origin
        self.twin = None
        self.next = None
        self.face: Face | None = None


    def __repr__(self):
        
        origin_ind = self.origin.index if self.origin is not None else None
        return f"HalfEdge(origin={origin_ind})"