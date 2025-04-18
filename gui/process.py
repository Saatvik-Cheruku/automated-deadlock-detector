from typing import List, Set, Tuple, Optional

class Process:
    def __init__(self, name: str, position: Tuple[int, int]):
        self.name = name
        self.position = position
        self.requesting: Set['Resource'] = set()  # Resources this process is requesting
        self.allocated: Set['Resource'] = set()   # Resources allocated to this process
        self.color = (50, 205, 50)  # Default to lime green
        
    def request_resource(self, resource: 'Resource') -> None:
        """Request a resource"""
        if resource not in self.allocated:
            self.requesting.add(resource)
            resource.requested_by.add(self)
            
    def allocate_resource(self, resource: 'Resource') -> None:
        """Allocate a resource to this process"""
        if resource in self.requesting:
            self.requesting.remove(resource)
            resource.requested_by.remove(self)
        self.allocated.add(resource)
        resource.allocated_to = self
        
    def release_resource(self, resource: 'Resource') -> None:
        """Release an allocated resource"""
        if resource in self.allocated:
            self.allocated.remove(resource)
            resource.allocated_to = None
        
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        """Check if a point is within this process's circle"""
        x, y = pos
        center_x = self.position[0] + 25  # Circle center x (25 is radius)
        center_y = self.position[1] + 25  # Circle center y
        return (x - center_x) ** 2 + (y - center_y) ** 2 <= 25 ** 2
        
    def __repr__(self) -> str:
        return f"Process({self.name})"

class Resource:
    def __init__(self, name: str, position: Tuple[int, int]):
        self.name = name
        self.position = position
        self.allocated_to: Optional[Process] = None  # Process this resource is allocated to
        self.requested_by: Set[Process] = set()      # Processes requesting this resource
        
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        """Check if a point is within this resource's square"""
        x, y = pos
        return (self.position[0] <= x <= self.position[0] + 50 and  # 50x50 square
                self.position[1] <= y <= self.position[1] + 50)
                
    def __repr__(self) -> str:
        return f"Resource({self.name})" 