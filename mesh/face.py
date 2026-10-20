class Face:

    def __init__(self, index):
        self.half_edge = None
        self.index = index


    def __repr__(self):
        return f"Face({self.index})"