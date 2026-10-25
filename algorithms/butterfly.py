import numpy as np

from mesh.vertex import Vertex
from mesh.face import Face
from mesh.half_edge import HalfEdge
from mesh.mesh import Mesh

import math

class ButterflySubdivision():

    def __init__(self, input_mesh: Mesh):
        boundary_edges = [
            edge for edge in input_mesh.half_edges
            if edge.twin is None
        ]

        print("Vertices:", len(input_mesh.vertices))
        print("Faces:", len(input_mesh.faces))
        print("Half-edges:", len(input_mesh.half_edges))
        print("Unique edges:", len(input_mesh.get_unique_edges()))
        print("Boundary half-edges:", len(boundary_edges))
        self.input_mesh = input_mesh


    def subdivide(self)->Mesh:
        print("Butterfly subdivide() called")

        self.unique_edges = self.input_mesh.get_unique_edges()
        print("Unique edges:", len(self.unique_edges))

        self.identify_boundary_vertices_and_edges()
        print("Boundary edges:", len(self.boundary_edges))

        self.calculate_neighbours()
        self.create_edge_vertices()


        triangles = []
        for face in self.input_mesh.faces:
            triangles.extend(self.split_face_into_triangles(face))

        faces = []
        half_edges = []
        for index, triangle in enumerate(triangles):
            face = Face(index)
            faces.append(face)
            face_half_edges = []
            
            for vertex in triangle:
                half_edge = HalfEdge(vertex)
                half_edges.append(half_edge)
                half_edge.face = face
                face_half_edges.append(half_edge)

            for i in range(len(face_half_edges)):
                face_half_edges[i].next = face_half_edges[(i + 1) % len(face_half_edges)]

            face.half_edge = face_half_edges[0]
        
        mesh = Mesh(self.list_vertices(), half_edges, faces)
        mesh.connect_half_edges()

        return mesh


    def find_boundary_neighbors(self, vertex):
        neighbors = set()

        for edge in self.boundary_edges:
            start = edge.origin
            end = edge.next.origin

            if start == vertex:
                neighbors.add(end)
            elif end == vertex:
                neighbors.add(start)

        return neighbors

    def calculate_neighbours(self):
        self.neighbours = {vertex.index: set() for vertex in self.input_mesh.vertices}

        for edge in self.unique_edges:
            a = edge.origin.index
            b = edge.next.origin.index
            self.neighbours[a].add(b)
            self.neighbours[b].add(a)


    def list_vertices(self):
        new_vertices = self.input_mesh.vertices.copy()
        new_vertices.extend(self.edge_vertices.values())
        return new_vertices

    def split_face_into_triangles(self, face):
        
        A = face.half_edge.origin
        B = face.half_edge.next.origin
        C = face.half_edge.next.next.origin

        M_AB = self.edge_vertices[tuple(sorted((A.index, B.index)))]
        M_BC = self.edge_vertices[tuple(sorted((B.index, C.index)))]
        M_CA = self.edge_vertices[tuple(sorted((C.index, A.index)))]


        triangles = []

        
        triangles.append((A, M_AB, M_CA))
        triangles.append((M_AB, B, M_BC))
        triangles.append((M_CA, M_BC, C))
        triangles.append((M_AB, M_BC, M_CA))
        return triangles

    
    def create_edge_vertices(self):
        print("create_edge_vertices() called")
        self.edge_vertices = {}

        index = len(self.input_mesh.vertices)

        for edge in self.unique_edges:
            A = edge.origin
            B = edge.next.origin

            print(f"\nEdge: {A.index} -> {B.index}")

            if edge.twin is None:
                print("Using boundary rule")
                x = self.boundary_edge_position(edge)
            else:
                valence_A = len(self.neighbours[A.index])
                valence_B = len(self.neighbours[B.index])

                boundary_A = A in self.boundary_vertices
                boundary_B = B in self.boundary_vertices

                print(
                    f"Valence A={valence_A}, B={valence_B}; "
                    f"boundary A={boundary_A}, B={boundary_B}"
                )

                if boundary_A or boundary_B:
                    print("Using regular rule because of boundary vertex")
                    x = self.regular_butterfly_position(edge)

                elif valence_A != 6:
                    print(f"Using extraordinary rule for A={A.index}")
                    x = self.extraordinary_edge_rule(edge, A)

                elif valence_B != 6:
                    print(f"Using extraordinary rule for B={B.index}")
                    x = self.extraordinary_edge_rule(edge.twin, B)

                else:
                    print("Using regular Butterfly rule")
                    x = self.regular_butterfly_position(edge)

            new_vertex = Vertex(index, x)
            index += 1

            key = tuple(sorted((A.index, B.index)))
            self.edge_vertices[key] = new_vertex

    def modified_butterfly_position(self, edge):
        A = edge.origin
        B = edge.next.origin

        valence_A = len(self.neighbours[A.index])
        valence_B = len(self.neighbours[B.index])

        extraordinary_A = valence_A != 6
        extraordinary_B = valence_B != 6

        if extraordinary_A and extraordinary_B:
            print(
                "Edge:", edge.origin.index, "->", edge.next.origin.index,
                "| twin:", edge.twin is not None,
                "| A valence:", len(self.neighbours[A.index]),
                "| B valence:", len(self.neighbours[B.index]),
            )
            x_A = self.extraordinary_edge_rule(edge, A)
            x_B = self.extraordinary_edge_rule(edge.twin, B)
            return 0.5 * (x_A + x_B)

        if extraordinary_A:
            print(
                "Edge:", edge.origin.index, "->", edge.next.origin.index,
                "| twin:", edge.twin is not None,
                "| A valence:", len(self.neighbours[A.index]),
                "| B valence:", len(self.neighbours[B.index]),
            )
            return self.extraordinary_edge_rule(edge, A)

        if extraordinary_B:
            return self.extraordinary_edge_rule(edge.twin, B)

        return self.regular_butterfly_position(edge)

    
    def extraordinary_edge_rule(self, edge, extraordinary_vertex):
        A = extraordinary_vertex
        B = edge.next.origin if edge.origin == A else edge.origin

        if A in self.boundary_vertices:
            return self.boundary_edge_position(edge) if edge.twin is None else (
                0.5 * (edge.origin.position + edge.next.origin.position)
            )

        neighbors = self.ordered_vertex_neighbors(A)
        k = len(neighbors)

        if B not in neighbors:
            raise ValueError(
                f"Vertex ring inconsistency: vertex {B.index} is not a "
                f"neighbor of extraordinary vertex {A.index}. "
                "Check Mesh.connect_half_edges() and half-edge next/twin links."
            )

        edge_index = neighbors.index(B)
        neighbors = neighbors[edge_index:] + neighbors[:edge_index]

        if k == 3:
            weights = [5 / 12, -1 / 12, -1 / 12]
        elif k == 4:
            weights = [3 / 8, 0, -1 / 8, 0]
        elif k >= 5:
            weights = [
                (1 / k) * (
                    1 / 4
                    + math.cos(2 * math.pi * i / k)
                    + 1 / 2 * math.cos(4 * math.pi * i / k)
                )
                for i in range(k)
            ]
        else:
            raise ValueError(f"Unsupported valence: {k}")

        x = 0.75 * A.position
        for weight, neighbor in zip(weights, neighbors):
            x = x + weight * neighbor.position

        return x

    def ordered_vertex_neighbors(self, vertex):
        outgoing = [
            h for h in self.input_mesh.half_edges
            if h.origin == vertex
        ]

        if not outgoing:
            raise ValueError(
                f"Vertex {vertex.index} has no outgoing half-edges"
            )

        neighbors = list(dict.fromkeys(
            h.next.origin for h in outgoing
        ))

        start = next(
            (h for h in outgoing if h.twin is not None),
            None
        )

        if start is None:
            return neighbors

        ordered = []
        visited = set()
        current = start

        while current not in visited:
            visited.add(current)
            ordered.append(current.next.origin)

            if current.twin is None:
                break

            current = current.twin.next

        if current == start and len(ordered) == len(neighbors):
            return ordered

        if set(ordered) != set(neighbors):
            print(
                f"Warning: incomplete ring for vertex {vertex.index}; "
                f"traversed {len(ordered)} of {len(neighbors)} neighbors."
            )

        return neighbors

    def extraordinary_weight(self, i, k):
        if k == 3:
            return 0.5 if i == 0 else -0.25

        if k == 4:
            return {0: 3/8, 1: 0, 2: -1/8, 3: 0}[i]

        if k > 5:
            return (
                1 / k
                * (
                    1/4
                    + math.cos(2 * math.pi * i / k)
                    + 1/2 * math.cos(4 * math.pi * i / k)
                )
            )

        raise ValueError(f"Unsupported valence: {k}")
    def boundary_edge_position(self, edge):
        A = edge.origin
        B = edge.next.origin

        neighbors_A = self.find_boundary_neighbors(A) - {B}
        neighbors_B = self.find_boundary_neighbors(B) - {A}

        if len(neighbors_A) != 1 or len(neighbors_B) != 1:
            raise ValueError("Invalid boundary edge configuration")

        L = next(iter(neighbors_A))
        R = next(iter(neighbors_B))

        return (
            (9 / 16) * (A.position + B.position)
            - (1 / 16) * (L.position + R.position)
        )

    def regular_butterfly_position(self, edge):
        A = edge.origin
        B = edge.next.origin

        if edge.twin is None:
            return self.boundary_edge_position(edge)

        C = edge.next.next.origin
        D = edge.twin.next.next.origin

        print("A:", A.index, A.position)
        print("B:", B.index, B.position)
        print("C:", C.index, C.position)
        print("D:", D.index, D.position)
        
        outer_edges = [
            edge.next,
            edge.next.next,
            edge.twin.next,
            edge.twin.next.next,
        ]

        outer_vertices = []

        for outer_edge in outer_edges:
            if outer_edge.twin is None:
                return 0.5 * (A.position + B.position)

            outer_vertices.append(
                outer_edge.twin.next.next.origin
            )

        E, F, G, H = outer_vertices

        return (
            0.5 * (A.position + B.position)
            + 0.125 * (C.position + D.position)
            - 0.0625 * (
                E.position + F.position + G.position + H.position
            )
        )


    def identify_boundary_vertices_and_edges(self):
        self.boundary_vertices = set()
        self.boundary_edges = set()
        self.boundary_dict = dict()

        for edge in self.input_mesh.half_edges:
            if edge.twin is None:
                start = edge.origin
                end = edge.next.origin

                self.boundary_edges.add(edge)
                self.boundary_vertices.update((start, end))
                self.boundary_dict[start.index] = end.index
    