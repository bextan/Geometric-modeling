

class HalfEdge:
    def __init__(self, origin):
        self.origin = origin
        self.twin = None
        self.next = None
        self.face = None


    def __repr__(self):
        
        origin_ind = self.origin.index if self.origin is not None else None
        return f"HalfEdge(origin={origin_ind})"