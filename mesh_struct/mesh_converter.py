import trimesh
from mesh import Mesh
from vertex import Vertex
from half_edge import HalfEdge
from face import Face

from pathlib import Path

def load_mesh(file_path):
    path = Path(file_path)

    if path.suffix.lower() not in (".stl", ".obj"):
        raise ValueError("Only STL and OBJ files are supported")
    
    mesh = trimesh.load(path, force="mesh")
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("The file did not produce a triangular mesh")

    vertices = []

    for index, position in enumerate(mesh.vertices):

        vertex = Vertex(index, position)
        vertices.append(vertex)

    faces = []
    half_edges = []

    for index, face_indices in enumerate(mesh.faces):
        face = Face(index)
        faces.append(face)


        face_half_edges = []

        for i in face_indices:
            half_edge = HalfEdge(vertices[i])
            half_edges.append(half_edge)
            half_edge.face = face
            face_half_edges.append(half_edge)

        for i in range(len(face_half_edges)):
            face_half_edges[i].next = face_half_edges[(i + 1) % len(face_half_edges)]

        face.half_edge = face_half_edges[0]

    edge_map = {}


    for half_edge in half_edges:
        start = half_edge.origin.index
        end = half_edge.next.origin.index

        if (end, start) in edge_map:
            twin = edge_map[(end, start)]
            half_edge.twin = twin
            twin.twin = half_edge
        else: 
            edge_map[(start, end)] = half_edge

        
    return Mesh(vertices, half_edges, faces)

def main():
    
    custom_mesh = load_mesh("files/jack-o-lantern-duck.stl")

    print("Vertices:", len(custom_mesh.vertices))
    print("Half-edges:", len(custom_mesh.half_edges))
    print("Faces:", len(custom_mesh.faces))


if __name__ == "__main__":
    main()