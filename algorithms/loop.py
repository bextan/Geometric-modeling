import numpy as np

from mesh.vertex import Vertex
from mesh.face import Face
from mesh.half_edge import HalfEdge
from mesh.mesh import Mesh

import math

class LoopSubdivision():
    def __init__(self, input_mesh: Mesh):
        self.input_mesh = input_mesh


    def subdivide(self, progress_callback=None) -> Mesh:
        self.report_progress(progress_callback, 10, "Getting unique edges...")
        self.unique_edges = self.input_mesh.get_unique_edges()

        self.report_progress(
            progress_callback, 25,
            "Identifying boundary vertices and edges..."
        )
        self.identify_boundary_vertices_and_edges()

        self.report_progress(progress_callback, 35, "Calculating neighbours...")
        self.calculate_neighbours()

        self.report_progress(progress_callback, 45, "Creating new vertices...")
        self.create_edge_vertices()

        self.report_progress(
            progress_callback, 60,
            "Repositioning original vertices..."
        )
        self.reposition_original_vertices()

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
                face_half_edges[i].next = face_half_edges[
                    (i + 1) % len(face_half_edges)
                ]

            face.half_edge = face_half_edges[0]

        mesh = Mesh(self.list_vertices(), half_edges, faces)
        mesh.connect_half_edges()

        self.report_progress(progress_callback, 100, "Finished!")
        return mesh
    @staticmethod
    def report_progress(callback, value, message):
        if callback is not None:
            callback(value, message)

    def reposition_original_vertices(self):
        new_positions = {}
        for vertex in self.input_mesh.vertices:
            if vertex not in self.boundary_vertices:
                valence = len(self.neighbours[vertex.index])
                loop_weight = (1 / valence) * (5/8 -(3/8 + 1/4*math.cos(2 * math.pi/valence)) ** 2)
                neighbor_positions = sum(
                    (self.input_mesh.vertices[i].position for i in self.neighbours[vertex.index]),start=np.zeros(3))
                new_position = (1 - valence*loop_weight)*vertex.position + loop_weight*neighbor_positions
            else:
                prev_vertex, next_vertex = self.find_boundary_neighbors(vertex)

                new_position = (3/4)*vertex.position + (1/8)*prev_vertex.position + (1/8)*next_vertex.position
            
            new_positions[vertex.index] = new_position

        for vertex in self.input_mesh.vertices:
            vertex.position = new_positions[vertex.index]

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
    
    def subdivide_faces(self):
        new_triangles = []

        for face in self.input_mesh.faces:
            new_triangles.extend(self.split_face_into_triangles(face))

        return new_triangles

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
        self.edge_vertices = dict()

        index = len(self.input_mesh.vertices)
        for unique_edge in self.unique_edges:
            if unique_edge.twin is not None:
                A_x = unique_edge.origin.position
                B_x = unique_edge.next.origin.position
                C_x = unique_edge.next.next.origin.position
                D_x = unique_edge.twin.next.next.origin.position

                E_x = (3 / 8) * (A_x + B_x) + (1 / 8) * (C_x + D_x)
            else:
                A_x = unique_edge.origin.position
                B_x = unique_edge.next.origin.position

                E_x = ((A_x+B_x)/2)
           
            new_vertex = Vertex(index, E_x)
            index+=1
            key = tuple(sorted((unique_edge.origin.index,unique_edge.next.origin.index)))
            self.edge_vertices[key] = new_vertex



    def identify_boundary_vertices_and_edges(self):
            self.boundary_vertices = set()
            self.boundary_edges = set()

            for half_edge in self.input_mesh.half_edges:
                if half_edge.twin is None:
                    self.boundary_edges.add(half_edge)
                    self.boundary_vertices.add(half_edge.origin)
                    self.boundary_vertices.add(half_edge.next.origin)


    