# Geometric Modeling: Triangulated Mesh Subdivision

A modular Python application developed for surface subdivision of 3D triangular meshes loaded from STL and OBJ files, fulfilling Project 1 requirements for Geometric Modeling.

---

## 📌 Project Overview
* **Objective**: Ingest 3D surface meshes from `.stl` and `.obj` formats, build internal topological adjacency representations, and execute surface refinement using both approximating and interpolating subdivision algorithms.
* **Core Technology**: 100% Python.
* **Subdivision Schemes**:
  * **Loop Subdivision**: Approximating triangular scheme based on quartic box splines. Calculates edge midpoints with quartic weighting and shifts existing vertices according to local topological valence.
  * **Modified Butterfly Subdivision**: Interpolating triangular scheme using an 8-point stencil for regular vertices (valence 6) and specialized weighting matrices for extraordinary vertices, preserving initial geometry coordinates.
* **Interactive Viewport**: Real-time rendering interface with solid-shaded and wireframe visualization, runtime performance/geometry infobar, and keyboard-driven controls.

---

## 🗂️ Project Architecture

```text
Geometric-modeling/
├── algorithms/       # Loop and Butterfly subdivision implementations
├── files/            # Input 3D models (.stl, .obj) & mesh converters
├── mesh/             # Half-edge / adjacency topological data structures
├── mesh_io/          # Robust file parsers and exporters for STL and OBJ
├── tests/            # Test suite for mesh consistency and view modes
├── ui/               # Viewport window, event handling, and runtime infobar
├── .gitignore        # Version control ignore list
├── AI_DISCLOSURE.md  # Detailed AI vs. self-written work attribution
├── main.py           # Application entry point
├── README.md         # Project documentation and guide
└── requirements.txt  # Project dependencies
```

---

## 🚀 Setup & Installation

### Requirements
* Python 3.10 or higher
* Recommended: Virtual environment (`venv` or `conda`)

### Quickstart
```bash
# 1. Clone repository
git clone <repository_url>
cd Geometric-modeling

# 2. Initialize and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python main.py
```

---

## 🎮 Interactive Viewport Controls

| Key / Action | Action Description |
| :--- | :--- |
| **`W`** | Toggle between Solid Shaded and Wireframe mesh rendering modes |
| **`Space` / `S`** | Execute one refinement step of the active subdivision scheme |
| **`1`** | Switch active scheme to **Loop Subdivision** (Approximating) |
| **`2`** | Switch active scheme to **Modified Butterfly Subdivision** (Interpolating) |
| **`R`** | Reset viewport to base (unrefined) mesh |
| **Left Click + Drag** | Orbit / rotate camera |
| **Scroll Wheel** | Zoom camera in / out |

---

## 📐 Mathematical Foundations

### 1. Loop Subdivision (Approximating Scheme)
Loop subdivision operates on triangular meshes and generates $C^2$ continuous surfaces on regular vertices ($C^1$ on extraordinary vertices).
* **New Edge Vertices**: Placed along interior edges shared by two faces $(v_0, v_1, v_2)$ and $(v_1, v_0, v_3)$:
  $$v_{\text{edge}} = \frac{3}{8}(v_0 + v_1) + \frac{1}{8}(v_2 + v_3)$$
* **Updated Old Vertices**: For an existing vertex $v$ with valence $n$ and neighboring vertices $v_1, \dots, v_n$:
  $$v' = (1 - n\beta)v + \beta \sum_{i=1}^n v_i$$
  where:
  $$\beta = \frac{1}{n}\left(\frac{5}{8} - \left(\frac{3}{8} + \frac{1}{4}\cos\left(\frac{2\pi}{n}\right)\right)^2\right)$$

### 2. Modified Butterfly Subdivision (Interpolating Scheme)
Butterfly subdivision preserves original vertex locations ($v' = v$) while inserting new edge vertices using an 8-point stencil:
* **Regular Edge (Valence 6-6)**:
  $$v_{\text{new}} = \frac{1}{2}(v_0 + v_1) + 2w(v_2 + v_3) - w(v_4 + v_5 + v_6 + v_7), \quad \text{with } w = \frac{1}{16}$$
* **Extraordinary Vertices**: Special weighting coefficients derived to prevent creases or unconstrained oscillations around vertices with valence $n \neq 6$.

---

## 📋 Project Workflow & Task Tracking (Trello)

The development lifecycle is tracked across three primary workflow milestones aligned with our Trello board:

```
[Phase 1: Setup & Mesh] ──► [Phase 2: Subdivision Algorithms] ──► [Phase 3: Integration & Testing]
```

### 1. Phase 1: Setup, Mesh Representation & 3D Viewer
* **Environment & Architecture**: Initialize project repository, virtual environment, dependencies, and modular layout.
* **Mesh Data Structure**: Design custom adjacency and half-edge topological representations for efficient neighbor/valence lookups.
* **File Ingestion**: Implement robust parsers for triangulated `.obj` and `.stl` files, including error handling for malformed or non-triangular inputs.
* **3D Viewer Setup**: Construct the interactive viewport capable of rendering imported triangular meshes with real-time orbital rotation and zoom.

### 2. Phase 2: Subdivision Algorithms
* **Loop Subdivision**: Implement approximating surface refinement with edge point stencils and valence-dependent vertex updates.
* **Butterfly Subdivision**: Implement interpolating surface refinement with 8-point stencils for regular vertices and modified weights for extraordinary vertices.
* **Interactive Scheme Controls**: Add runtime toggling between Loop and Butterfly subdivision, with step-by-step iteration triggers.
*(Optional extension: Third subdivision scheme if scaling to a 3-member team).*

### 3. Phase 3: Integration, Testing & Presentation
* **Pipeline Integration**: Unify file loading, mesh conversion, subdivision computation, and viewport rendering into a cohesive execution flow.
* **Correctness Validation**: Test subdivision continuity, topology preservation, and manifold integrity across at least two distinct 3D models.
* **Error Handling & UX**: Enhance loading feedback, infobar telemetry, and wireframe inspection modes.
* **Delivery & Midterm Demo**: Final acceptance testing, documentation (`README.md`, `AI_DISCLOSURE.md`), and slide presentation for the midterm evaluation.
---

## 🤖 AI vs. Self-Written Attribution Summary
In accordance with course academic integrity guidelines, all code contributions are tracked and categorized:
* **Core Mathematics & Topology (`mesh/`, `algorithms/`)**: 100% human-authored logic covering stencil definitions, vertex valence calculations, and half-edge topological lookups.
* **Parsers & Utilities (`mesh_io/`, `files/`)**: AI-assisted drafting for file format byte parsing, verified and adapted manually.
* **User Interface & Boilerplate (`ui/`)**: Hybrid authoring; AI assisted with window layout and event-loop boilerplate, while wireframe toggling and infobar metrics were written manually.

*For full line-by-line attribution and debugging notes, refer to [AI_DISCLOSURE.md](./AI_DISCLOSURE.md).*
