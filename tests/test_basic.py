
from mesh_struct.vertex import Vertex
from mesh_struct.half_edge import HalfEdge
from mesh_struct.face import Face
from mesh_struct.mesh import Mesh


def test_triangle_mesh():
    # Create vertices
    v0 = Vertex(0, [0.0, 0.0, 0.0])
    v1 = Vertex(1, [1.0, 0.0, 0.0])
    v2 = Vertex(2, [0.0, 1.0, 0.0])

    vertices = [v0, v1, v2]

    # Create half-edges with their origin vertices
    he0 = HalfEdge(v0)
    he1 = HalfEdge(v1)
    he2 = HalfEdge(v2)

    half_edges = [he0, he1, he2]

    # Create a face
    face = Face(0)
    faces = [face]

    # Connect half-edges around the triangle
    he0.next = he1
    he1.next = he2
    he2.next = he0

    # Assign the face
    he0.face = face
    he1.face = face
    he2.face = face
    face.half_edge = he0

    # Assign outgoing half-edges to vertices
    v0.half_edge = he0
    v1.half_edge = he1
    v2.half_edge = he2

    # Create the mesh
    mesh = Mesh(vertices, half_edges, faces)

    # Test collection sizes
    assert len(mesh.vertices) == 3
    assert len(mesh.half_edges) == 3
    assert len(mesh.faces) == 1

    # Test origins
    assert he0.origin is v0
    assert he1.origin is v1
    assert he2.origin is v2

    # Test next connections
    assert he0.next is he1
    assert he1.next is he2
    assert he2.next is he0
    assert he0.next.next.next is he0

    # Test face connections
    assert he0.face is face
    assert he1.face is face
    assert he2.face is face
    assert face.half_edge is he0

    # Test vertex connections
    assert v0.half_edge is he0
    assert v1.half_edge is he1
    assert v2.half_edge is he2

    # Boundary edges have no twins in this single triangle
    assert he0.twin is None
    assert he1.twin is None
    assert he2.twin is None

    # Test representation
    assert repr(he0) == "HalfEdge(origin=0)"
    assert repr(he1) == "HalfEdge(origin=1)"
    assert repr(he2) == "HalfEdge(origin=2)"


if __name__ == "__main__":
    test_triangle_mesh()
    print("All mesh tests passed!")
