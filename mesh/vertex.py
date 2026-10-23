import numpy as np


class Vertex:
    def __init__(self, index, position):
        
        position = np.asarray(position, dtype=float)
        
        # Position Validation
        if position.shape != (3,):
            raise ValueError("Position must contain exactly 3 coordinates.")
        
        if not np.isfinite(position).all():
            raise ValueError("Position coordinates must be finite.")
            
        self.position = position

        self.index = index
        self.half_edge = None
    
    def __repr__(self):
        return f"Vertex({self.index}, {self.position})"
    