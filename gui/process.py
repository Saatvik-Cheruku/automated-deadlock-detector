from typing import List, Set, Tuple, Optional

class Process:
    def __init__(self, name: str, position: Tuple[int, int], color=(50, 205, 50)):
        self.name = name
        self.position = position
        self.color = color
        self.original_color = color
        self.requesting = set()  # Set of resources this process is requesting
        self.allocated = set()   # Set of resources allocated to this process
        
    def request_resource(self, resource: 'Resource') -> bool:
        """Request a resource"""
        if resource not in self.allocated:
            self.requesting.add(resource)
            return True
        return False
        
    def allocate_resource(self, resource: 'Resource') -> bool:
        """Allocate a resource to this process"""
        if resource in self.requesting:
            self.requesting.remove(resource)
            self.allocated.add(resource)
            return True
        return False
        
    def release_resource(self, resource: 'Resource') -> bool:
        """Release an allocated resource"""
        if resource in self.allocated:
            self.allocated.remove(resource)
            return True
        return False
        
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is within this process's bounds"""
        x, y = point
        px, py = self.position
        # Assuming circular shape with radius 25
        dx = x - (px + 25)
        dy = y - (py + 25)
        return (dx * dx + dy * dy) <= 625  # 25^2
        
    def __repr__(self) -> str:
        return f"Process({self.name})"

class Resource:
    def __init__(self, name: str, position: Tuple[int, int], color=(200, 50, 50)):
        self.name = name
        self.position = position
        self.color = color
        self.original_color = color
        self.allocated_to: Optional[Process] = None  # Process this resource is allocated to
        self.requested_by: Set[Process] = set()      # Processes requesting this resource
        
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is within this resource's bounds"""
        x, y = point
        rx, ry = self.position
        # Assuming square shape with side 50
        return (rx <= x <= rx + 50) and (ry <= y <= ry + 50)
                
    def __repr__(self) -> str:
        return f"Resource({self.name})" 