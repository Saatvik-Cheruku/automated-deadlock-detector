from typing import Dict, List, Set, Tuple, Optional
from gui.process import Process, Resource

class DeadlockDetector:
    def __init__(self):
        self.processes: Dict[str, Process] = {}
        self.resources: Dict[str, Resource] = {}
        self.process_counter = 1
        self.resource_counter = 1

    def add_process(self, position: Tuple[int, int]) -> Process:
        """Add a new process to the system"""
        name = f"P{self.process_counter}"
        self.process_counter += 1
        process = Process(name, position)
        self.processes[name] = process
        return process

    def add_resource(self, position: Tuple[int, int]) -> Resource:
        """Add a new resource to the system"""
        name = f"R{self.resource_counter}"
        self.resource_counter += 1
        resource = Resource(name, position)
        self.resources[name] = resource
        return resource

    def remove_process(self, process: Process):
        """Remove a process and all its edges"""
        if process.name in self.processes:
            # Remove all allocations and requests
            for resource in process.allocated:
                resource.allocated_to.remove(process)
            for resource in process.requesting:
                resource.requested_by.remove(process)
            del self.processes[process.name]

    def remove_resource(self, resource: Resource):
        """Remove a resource and all its edges"""
        if resource.name in self.resources:
            # Remove all allocations and requests
            if resource.allocated_to:  # Check if resource is allocated to a process
                resource.allocated_to.allocated.remove(resource)
            for process in resource.requested_by:
                process.requesting.remove(resource)
            del self.resources[resource.name]

    def detect_deadlock(self):
        """
        Detect if there is a deadlock in the system.
        Returns a tuple (bool, set) where the bool indicates if there is a deadlock,
        and the set contains the processes involved in the deadlock.
        """
        # Build adjacency list representation of the graph
        graph = {process: [] for process in self.processes.values()}
        
        # Add edges from process to process through resources
        for process in self.processes.values():
            for resource in process.requesting:
                if resource.allocated_to:  # Only add edge if resource is allocated
                    graph[process].append(resource.allocated_to)
        
        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        deadlocked = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        deadlocked.add(neighbor)
                        return True
                elif neighbor in rec_stack:
                    deadlocked.add(neighbor)
                    return True
                    
            rec_stack.remove(node)
            return False
            
        # Run DFS from each unvisited node
        for process in self.processes.values():
            if process not in visited:
                if dfs(process):
                    deadlocked.add(process)
                    
        return len(deadlocked) > 0, deadlocked 