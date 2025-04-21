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
                resource.allocated_to = None
            for resource in process.requesting:
                resource.requested_by.remove(process)
            
            # Get the number of the removed process
            removed_num = int(process.name[1:])
            del self.processes[process.name]
            
            # Renumber remaining processes
            processes_to_rename = {}
            for p in self.processes.values():
                num = int(p.name[1:])
                if num > removed_num:
                    new_name = f"P{num-1}"
                    processes_to_rename[p.name] = (p, new_name)
            
            # Apply renaming
            for old_name, (proc, new_name) in processes_to_rename.items():
                proc.name = new_name
                self.processes[new_name] = proc
                del self.processes[old_name]
            
            # Update counter
            self.process_counter = max(1, len(self.processes) + 1)

    def remove_resource(self, resource: Resource):
        """Remove a resource and all its edges"""
        if resource.name in self.resources:
            # Remove all allocations and requests
            if resource.allocated_to:
                resource.allocated_to.allocated.remove(resource)
            for process in resource.requested_by:
                process.requesting.remove(resource)
            
            # Get the number of the removed resource
            removed_num = int(resource.name[1:])
            del self.resources[resource.name]
            
            # Renumber remaining resources
            resources_to_rename = {}
            for r in self.resources.values():
                num = int(r.name[1:])
                if num > removed_num:
                    new_name = f"R{num-1}"
                    resources_to_rename[r.name] = (r, new_name)
            
            # Apply renaming
            for old_name, (res, new_name) in resources_to_rename.items():
                res.name = new_name
                self.resources[new_name] = res
                del self.resources[old_name]
            
            # Update counter
            self.resource_counter = max(1, len(self.resources) + 1)

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
        
    def clear_graph(self):
        """Clear all processes and resources from the system"""
        self.processes.clear()
        self.resources.clear()
        self.process_counter = 1
        self.resource_counter = 1 