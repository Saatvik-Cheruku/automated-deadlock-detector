import pygame
from gui.node import Node
from gui.edge import Edge
from typing import List, Optional, Tuple

class Graph:
    def __init__(self):
        """Initialize an empty graph."""
        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.mode = "process"  # Default mode for node creation
        
    def add_node(self, node_type: str, position: Tuple[int, int]) -> None:
        """Add a new node to the graph."""
        node = Node(position, node_type)
        self.nodes.append(node)
        
    def add_edge(self, start: Node, end: Node) -> None:
        """Add a new edge between two nodes."""
        # Determine edge type based on node types
        if start.type == 'process' and end.type == 'resource':
            edge_type = 'request'
        elif start.type == 'resource' and end.type == 'process':
            edge_type = 'allocation'
        else:
            return  # Invalid edge type
            
        edge = Edge(start, end, edge_type)
        if edge not in self.edges:
            self.edges.append(edge)
            
    def remove_node(self, node: Node) -> None:
        """Remove a node and all its connected edges."""
        self.edges = [e for e in self.edges if e.start != node and e.end != node]
        self.nodes.remove(node)
        
    def get_node_at_position(self, position: Tuple[int, int]) -> Optional[Node]:
        """Return the node at the given position, if any."""
        for node in self.nodes:
            if node.contains_point(position):
                return node
        return None
        
    def handle_click(self, position: Tuple[int, int]) -> None:
        """Handle mouse click events."""
        clicked_node = self.get_node_at_position(position)
        
        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
                clicked_node.selected = True
            else:
                if self.selected_node != clicked_node:
                    self.add_edge(self.selected_node, clicked_node)
                self.selected_node.selected = False
                self.selected_node = None
        else:
            if self.selected_node:
                self.selected_node.selected = False
                self.selected_node = None
            else:
                self.add_node(self.mode, position)
                
    def handle_right_click(self, position: Tuple[int, int]) -> None:
        """Handle right-click events (node deletion)."""
        clicked_node = self.get_node_at_position(position)
        if clicked_node:
            self.remove_node(clicked_node)
            
    def set_mode(self, mode: str) -> None:
        """Set the current node creation mode."""
        self.mode = mode
        
    def has_cycle(self) -> bool:
        """Check if the graph contains a cycle (deadlock)."""
        visited = set()
        path = set()
        
        def dfs(node: Node) -> bool:
            visited.add(node)
            path.add(node)
            
            # Get all nodes that this node has edges to
            neighbors = [e.end for e in self.edges if e.start == node]
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in path:
                    return True
                    
            path.remove(node)
            return False
            
        # Start DFS from each unvisited node
        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
                    
        return False
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the entire graph."""
        # Draw edges first
        for edge in self.edges:
            edge.draw(screen)
            
        # Draw nodes on top
        for node in self.nodes:
            node.draw(screen) 