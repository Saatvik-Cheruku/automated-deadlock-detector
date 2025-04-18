from typing import List, Set, Dict, Optional
from .node import Node
from .edge import Edge

class Graph:
    def __init__(self):
        """Initialize an empty graph."""
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.process_count = 0
        self.resource_count = 0
        
    def add_node(self, node_type: str, position: tuple) -> Node:
        """Add a new node to the graph."""
        if node_type == 'process':
            node_id = f'P{self.process_count}'
            self.process_count += 1
        else:
            node_id = f'R{self.resource_count}'
            self.resource_count += 1
            
        node = Node(node_id, node_type, position)
        self.nodes.append(node)
        return node
    
    def add_edge(self, start: Node, end: Node, edge_type: str) -> bool:
        """Add a new edge to the graph if it doesn't already exist."""
        # Check if edge already exists
        for edge in self.edges:
            if (edge.start == start and edge.end == end) or \
               (edge.start == end and edge.end == start):
                return False
                
        edge = Edge(start, end, edge_type)
        self.edges.append(edge)
        return True
    
    def remove_node(self, node: Node) -> None:
        """Remove a node and all its connected edges."""
        if node in self.nodes:
            self.nodes.remove(node)
            self.edges = [edge for edge in self.edges 
                         if edge.start != node and edge.end != node]
    
    def remove_edge(self, edge: Edge) -> None:
        """Remove an edge from the graph."""
        if edge in self.edges:
            self.edges.remove(edge)
    
    def get_node_at_position(self, pos: tuple) -> Optional[Node]:
        """Get the node at a specific position if it exists."""
        for node in self.nodes:
            if node.is_clicked(pos):
                return node
        return None
    
    def detect_deadlock(self) -> bool:
        """
        Detect deadlock using DFS cycle detection.
        Returns True if a deadlock is detected, False otherwise.
        """
        visited: Set[Node] = set()
        recursion_stack: Set[Node] = set()
        
        def dfs(node: Node) -> bool:
            """Depth-first search to detect cycles."""
            visited.add(node)
            recursion_stack.add(node)
            
            # Get all outgoing edges from this node
            for edge in self.edges:
                if edge.start == node:
                    neighbor = edge.end
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in recursion_stack:
                        return True
                        
            recursion_stack.remove(node)
            return False
        
        # Check each unvisited node
        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
                    
        return False
    
    def draw(self, screen) -> None:
        """Draw all nodes and edges on the screen."""
        # Draw edges first (so they appear behind nodes)
        for edge in self.edges:
            edge.draw(screen)
            
        # Draw nodes
        for node in self.nodes:
            node.draw(screen)
    
    def reset(self) -> None:
        """Reset the graph to its initial state."""
        self.nodes.clear()
        self.edges.clear()
        self.process_count = 0
        self.resource_count = 0 