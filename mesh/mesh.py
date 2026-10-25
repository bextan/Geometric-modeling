from mesh.face import Face
from mesh.half_edge import HalfEdge
from mesh.vertex import Vertex
class Mesh:

    def __init__(self, vertices=None, half_edges=None, faces=None):
        self.vertices = vertices if vertices is not None else []
        self.half_edges = half_edges if half_edges is not None else []
        self.faces = faces if faces is not None else []


    def __repr__(self):
            
            return (
                f"Mesh(vertices={len(self.vertices)}, "
                f"half_edges={len(self.half_edges)}, "
                f"faces={len(self.faces)})"
            )

    def build_vertices(self, vertices_list):
        for index, position in enumerate(vertices_list):
            vertex = Vertex(index, position)
            self.vertices.append(vertex)

    def build_faces_and_halfedges(self, faces_list):
        for index, face_indices in enumerate(faces_list):
            if len(face_indices) != 3:
                raise ValueError("Each face must have exactly 3 vertices")
            
            face = Face(index)
            self.faces.append(face)

            face_half_edges = []
            
            for i in face_indices:
                half_edge = HalfEdge(self.vertices[i])
                self.half_edges.append(half_edge)
                half_edge.face = face
                face_half_edges.append(half_edge)

            for i in range(len(face_half_edges)):
                face_half_edges[i].next = face_half_edges[(i + 1) % len(face_half_edges)]

            face.half_edge = face_half_edges[0]
    
    # def build_faces_and_halfedges(self, triangle):
    #         face = Face(len(self.faces))
    
    #         face_half_edges = []
            
                        
    #         for vertex in triangle:
    #             half_edge = HalfEdge(vertex)
    #             self.half_edges.append(half_edge)
    #             half_edge.face = face
    #             face_half_edges.append(half_edge)
    
    #         for i in range(len(face_half_edges)):
    #             face_half_edges[i].next = face_half_edges[(i + 1) % len(face_half_edges)]
    
    #         face.half_edge = face_half_edges[0]
    #         self.faces.append(face)
    
    def connect_half_edges(self):
        edge_map = {}
        for half_edge in self.half_edges:
            start = half_edge.origin.index
            end = half_edge.next.origin.index

            if (end, start) in edge_map:
                twin = edge_map[(end, start)]
                half_edge.twin = twin
                twin.twin = half_edge
            else: 
                edge_map[(start, end)] = half_edge

    def get_unique_edges(self):
        unique_edges = {}

        for half_edge in self.half_edges:
            start = half_edge.origin.index
            end = half_edge.next.origin.index

            key = tuple(sorted((start, end)))
            unique_edges[key] = half_edge

        return list(unique_edges.values())

    

    