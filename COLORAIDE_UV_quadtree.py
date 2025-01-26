"""UV space quadtree for optimized face lookup."""
from mathutils import Vector
from typing import List, Tuple, Optional
import numpy as np

class UVBounds:
    """Represents UV coordinate boundaries"""
    def __init__(self, min_u=0.0, min_v=0.0, max_u=1.0, max_v=1.0):
        self.min_u = min_u
        self.min_v = min_v
        self.max_u = max_u
        self.max_v = max_v
        
    def center(self) -> Tuple[float, float]:
        """Get center point of bounds"""
        return ((self.min_u + self.max_u) * 0.5,
                (self.min_v + self.max_v) * 0.5)
                
    def contains(self, u: float, v: float) -> bool:
        """Check if point is within bounds"""
        return (self.min_u <= u <= self.max_u and 
                self.min_v <= v <= self.max_v)
                
    def intersects(self, other: 'UVBounds') -> bool:
        """Check if bounds intersect with other bounds"""
        return not (other.min_u > self.max_u or
                   other.max_u < self.min_u or
                   other.min_v > self.max_v or
                   other.max_v < self.min_v)

class UVFace:
    """Stores face data and UV coordinates"""
    def __init__(self, face_index: int, uvs: List[Vector], bounds: UVBounds):
        self.face_index = face_index
        self.uvs = uvs
        self.bounds = bounds
        
    def contains_point(self, u: float, v: float, epsilon=1e-5) -> bool:
        """Check if point is inside face using point-in-triangle test"""
        def area(x1, y1, x2, y2, x3, y3):
            return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2))/2.0)
            
        # Quick bounds check first
        if not self.bounds.contains(u, v):
            return False
            
        p = Vector((u, v))
        
        # Handle triangles and quads
        if len(self.uvs) == 3:
            A = area(self.uvs[0].x, self.uvs[0].y,
                    self.uvs[1].x, self.uvs[1].y,
                    self.uvs[2].x, self.uvs[2].y)
            A1 = area(p.x, p.y,
                     self.uvs[1].x, self.uvs[1].y,
                     self.uvs[2].x, self.uvs[2].y)
            A2 = area(self.uvs[0].x, self.uvs[0].y,
                     p.x, p.y,
                     self.uvs[2].x, self.uvs[2].y)
            A3 = area(self.uvs[0].x, self.uvs[0].y,
                     self.uvs[1].x, self.uvs[1].y,
                     p.x, p.y)
            return abs(A - (A1 + A2 + A3)) < epsilon
            
        elif len(self.uvs) == 4:
            # Split quad into two triangles
            return (self._point_in_triangle(p, self.uvs[0], self.uvs[1], self.uvs[2], epsilon) or
                   self._point_in_triangle(p, self.uvs[2], self.uvs[3], self.uvs[0], epsilon))
        
        return False
        
    def _point_in_triangle(self, p: Vector, a: Vector, b: Vector, c: Vector, epsilon: float) -> bool:
        """Helper for point-in-triangle test"""
        def area(x1, y1, x2, y2, x3, y3):
            return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2))/2.0)
            
        A = area(a.x, a.y, b.x, b.y, c.x, c.y)
        A1 = area(p.x, p.y, b.x, b.y, c.x, c.y)
        A2 = area(a.x, a.y, p.x, p.y, c.x, c.y)
        A3 = area(a.x, a.y, b.x, b.y, p.x, p.y)
        return abs(A - (A1 + A2 + A3)) < epsilon

class UVQuadtreeNode:
    """Node in UV quadtree"""
    def __init__(self, bounds: UVBounds, max_depth: int = 8, max_faces: int = 4):
        self.bounds = bounds
        self.max_depth = max_depth
        self.max_faces = max_faces
        self.depth = 0
        self.faces: List[UVFace] = []
        self.children = None
        
    def subdivide(self):
        """Split node into four children"""
        center_u, center_v = self.bounds.center()
        
        self.children = [
            UVQuadtreeNode(UVBounds(self.bounds.min_u, self.bounds.min_v, 
                                   center_u, center_v), 
                          self.max_depth, self.max_faces),
            UVQuadtreeNode(UVBounds(center_u, self.bounds.min_v,
                                   self.bounds.max_u, center_v),
                          self.max_depth, self.max_faces),
            UVQuadtreeNode(UVBounds(self.bounds.min_u, center_v,
                                   center_u, self.bounds.max_v),
                          self.max_depth, self.max_faces),
            UVQuadtreeNode(UVBounds(center_u, center_v,
                                   self.bounds.max_u, self.bounds.max_v),
                          self.max_depth, self.max_faces)
        ]
        
        for child in self.children:
            child.depth = self.depth + 1
            
        # Redistribute faces to children
        for face in self.faces:
            for child in self.children:
                if child.bounds.intersects(face.bounds):
                    child.insert(face)
                    
        self.faces.clear()
        
    def insert(self, face: UVFace):
        """Insert face into quadtree"""
        if not self.bounds.intersects(face.bounds):
            return
            
        if self.children is not None:
            for child in self.children:
                child.insert(face)
            return
            
        self.faces.append(face)
        
        # Check if we need to subdivide
        if len(self.faces) > self.max_faces and self.depth < self.max_depth:
            self.subdivide()
            
    def find_face(self, u: float, v: float) -> Optional[UVFace]:
        """Find face containing UV coordinate"""
        if not self.bounds.contains(u, v):
            return None
            
        # Check children first if they exist
        if self.children is not None:
            for child in self.children:
                face = child.find_face(u, v)
                if face is not None:
                    return face
            return None
            
        # Check faces in this node
        for face in self.faces:
            if face.contains_point(u, v):
                return face
                
        return None

class UVQuadtree:
    """UV space quadtree for optimized face lookup"""
    def __init__(self, max_depth: int = 8, max_faces: int = 4):
        self.root = UVQuadtreeNode(UVBounds(), max_depth, max_faces)
        
    def build_from_mesh(self, mesh):
        """Build quadtree from mesh UV data"""
        if not mesh.uv_layers.active:
            return
            
        uv_layer = mesh.uv_layers.active
        
        for poly in mesh.polygons:
            # Get UV coordinates for face
            uvs = [Vector(uv_layer.data[loop_idx].uv) 
                  for loop_idx in poly.loop_indices]
            
            # Calculate UV bounds
            u_coords = [uv.x for uv in uvs]
            v_coords = [uv.y for uv in uvs]
            bounds = UVBounds(min(u_coords), min(v_coords),
                            max(u_coords), max(v_coords))
                            
            # Create face and insert into tree
            face = UVFace(poly.index, uvs, bounds)
            self.root.insert(face)
            
    def find_face(self, u: float, v: float) -> Optional[UVFace]:
        """Find face containing UV coordinate"""
        return self.root.find_face(u, v)