import numpy as np

from mesh.vertex import Vertex
from mesh.face import Face
from mesh.half_edge import HalfEdge
from mesh.mesh import Mesh

import math

class ButterflySubdivision():

    def __init__(self, input_mesh: Mesh):
        self.input_mesh = input_mesh


    @staticmethod
    def report_progress(callback, value, message):
        if callback is not None:
            callback(value, message)
            
    def subdivide(self, progress_callback=None)->Mesh:
        self.report_progress(progress_callback, 10, "Getting unique edges...")
        self.unique_edges = self.input_mesh.get_unique_edges()
        self.report_progress( progress_callback, 25,"Identifying boundary topology...")
        self.identify_boundary_topology()
        self.report_progress(progress_callback, 45, "Calculating valences...")
        self.calculate_vertex_valences()
        self.report_progress(progress_callback, 45, "Creating new vertices...")
        self.create_edge_vertices()


        self.report_progress(progress_callback, 75, "Splitting into triangles...")
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

        self.report_progress(progress_callback, 100, "Finished!")
        return mesh

    def identify_boundary_topology(self):
        self.boundary_vertices = set()
        self.boundary_edges = set()
        self.boundary_next = {}
        self.boundary_prev = {}

        for edge in self.input_mesh.half_edges:
            if edge.twin is None:
                start = edge.origin
                end = edge.next.origin
                self.boundary_edges.add(edge)
                self.boundary_vertices.add(start.index)
                self.boundary_vertices.add(end.index)
                self.boundary_next[start.index] = end
                self.boundary_prev[end.index] = start

    def calculate_vertex_valences(self):
        self.valences = {v.index: 0 for v in self.input_mesh.vertices}
        for edge in self.unique_edges:
            self.valences[edge.origin.index]+=1
            self.valences[edge.next.origin.index]+=1

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
        self.edge_vertices = {}

        index = len(self.input_mesh.vertices)

        for edge in self.unique_edges:
            A = edge.origin
            B = edge.next.origin


            if edge.twin is None:
                x = self.boundary_edge_position(edge)
            else:
                x = self.modified_butterfly_position(edge)

            new_vertex = Vertex(index, x)
            index+=1

            key = tuple(sorted((A.index, B.index)))
            self.edge_vertices[key]= new_vertex

    def boundary_edge_position(self, edge):
        A = edge.origin
        B = edge.next.origin

        prev_A = self.boundary_prev.get(A.index)
        prev_B = self.boundary_next.get(B.index)

        A_p = A.position
        B_p = B.position
        # Отражение (reflection), если цепочка границы разомкнута
        prev_A_p = prev_A.position if prev_A is not None else (2.0 * A_p - B_p)
        prev_B_p = prev_B.position if prev_B is not None else (2.0 * B_p - A_p)

        new_pos = (9.0/16.0)*(A_p + B_p) - (1.0/16.0)*(prev_A_p + prev_B_p)

        return new_pos
    def modified_butterfly_position(self, edge):
        A = edge.origin
        B = edge.next.origin

        if (A.index not in self.boundary_vertices and self.valences[A.index] != 6
            and B.index not in self.boundary_vertices and self.valences[B.index] != 6):
            pos_A = self.extraordinary_edge_rule(edge, A)
            pos_B = self.extraordinary_edge_rule(edge.twin, B)
            return 0.5*(pos_A + pos_B)
        
        elif A.index not in self.boundary_vertices and self.valences[A.index] != 6:
            return self.extraordinary_edge_rule(edge, A)
        elif B.index not in self.boundary_vertices and self.valences[B.index] != 6:
            return self.extraordinary_edge_rule(edge.twin, B)
        else:
            return self.regular_butterfly_position(edge)

    
    def extraordinary_edge_rule(self, edge, extraordinary_vertex):
        A = extraordinary_vertex

        neighbors = []
        cur = edge
        while True:
            neighbors.append(cur.next.origin)
            if cur.twin is None:
                break
            cur = cur.twin.next
            if cur == edge:
                break

        k = len(neighbors)

        pos = 0.75 * A.position
        ind = 0

        weights = []
        if k == 3:
            weights = [5.0 / 12.0, -1.0 / 12.0, -1.0 / 12.0]
        elif k == 4:
            weights= [3.0 / 8.0, 0.0, -1.0 / 8.0, 0.0]
        elif k >= 5:
            weights = [(1.0 / k) * (0.25+ math.cos(2.0 * math.pi * i / k)+ 0.5 * math.cos(4.0 * math.pi * i / k)) for i in range(k)]
        else:
            weights = [1.0 / k] * k
        
        for neighbor in neighbors:
            pos = pos + weights[ind] * neighbor.position
            ind+=1
        return pos

    def regular_butterfly_position(self, edge):
        A = edge.origin
        B = edge.next.origin

        if edge.twin is None:
            return self.boundary_edge_position(edge)

        C = edge.next.next.origin
        D = edge.twin.next.next.origin

        
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

    