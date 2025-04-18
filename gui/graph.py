import pygame
from typing import List, Dict, Set, Optional, Tuple
from gui.node import Node
from gui.edge import Edge

class Graph:
    def __init__(self):
        """Initialize an empty graph."""
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.selected_node: Optional[Node] = None
        self.mode = "process"  # Default mode for node creation
        self.deadlock_nodes = set()  # Store nodes involved in deadlock
        
    def add_node(self, node_type: str, position: Tuple[int, int]) -> None:
        """Add a new node to the graph."""
        x, y = position
        node = Node(x, y, node_type)
        self.nodes.append(node)
        
    def add_edge(self, start: Node, end: Node) -> None:
        """Add a new edge between two nodes."""
        # Don't add edge if it already exists
        for edge in self.edges:
            if edge.start == start and edge.end == end:
                return
        self.edges.append(Edge(start, end))
        
    def remove_node(self, node: Node) -> None:
        """Remove a node and all its connected edges from the graph."""
        # Remove all edges connected to this node
        self.edges = [edge for edge in self.edges 
                     if edge.start != node and edge.end != node]
        # Remove the node
        self.nodes.remove(node)
        self.deadlock_nodes.discard(node)
        
    def get_node_at(self, position: Tuple[int, int]) -> Optional[Node]:
        """Get the node at the given position, if any."""
        for node in self.nodes:
            if node.contains_point(*position):
                return node
        return None
        
    def handle_click(self, position: Tuple[int, int]) -> None:
        """Handle a left click at the given position."""
        clicked_node = self.get_node_at(position)
        
        if clicked_node:
            if self.selected_node:
                # If we already had a node selected, create an edge
                if self.selected_node != clicked_node:
                    self.add_edge(self.selected_node, clicked_node)
                self.selected_node.selected = False
                self.selected_node = None
            else:
                # Select the clicked node
                self.selected_node = clicked_node
                clicked_node.selected = True
        else:
            # If we click empty space, add a new node
            self.add_node(self.mode, position)
            if self.selected_node:
                self.selected_node.selected = False
                self.selected_node = None
                
    def handle_right_click(self, position: Tuple[int, int]) -> None:
        """Handle a right click at the given position."""
        node = self.get_node_at(position)
        if node:
            self.remove_node(node)
            if self.selected_node == node:
                self.selected_node = None
                
    def set_mode(self, mode: str) -> None:
        """Set the current node creation mode."""
        self.mode = mode
        
    def has_cycle(self) -> bool:
        """Check if the graph contains a cycle (deadlock) and highlight it."""
        visited = set()
        path = set()
        self.deadlock_nodes.clear()  # Clear previous deadlock
        
        def dfs(node: Node) -> bool:
            visited.add(node)
            path.add(node)
            
            for edge in self.edges:
                if edge.start == node:
                    next_node = edge.end
                    if next_node not in visited:
                        if dfs(next_node):
                            if not self.deadlock_nodes:  # Only add if not already found
                                self.deadlock_nodes.add(node)
                            next_node.in_deadlock = True
                            return True
                    elif next_node in path:
                        # We found a cycle, add all nodes in the cycle to deadlock_nodes
                        current = node
                        while current != next_node:
                            self.deadlock_nodes.add(current)
                            current = self.get_previous_node(current)
                        self.deadlock_nodes.add(next_node)
                        return True
            
            path.remove(node)
            return False
            
        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False
        
    def get_previous_node(self, node: Node) -> Node:
        """Get the previous node in the cycle."""
        for edge in self.edges:
            if edge.end == node:
                return edge.start
        return node
        
    def clear(self) -> None:
        """Clear the graph."""
        self.nodes.clear()
        self.edges.clear()
        self.selected_node = None
        self.deadlock_nodes.clear()
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the graph on the screen."""
        # Draw edges first (under nodes)
        for edge in self.edges:
            edge.draw(screen)
            
        # Draw nodes on top
        for node in self.nodes:
            node.draw(screen) 