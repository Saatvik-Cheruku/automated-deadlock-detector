import pygame
from typing import Tuple, List
from .utils import WHITE, BLACK, YELLOW

class Node:
    def __init__(self, node_id: str, node_type: str, position: Tuple[int, int], radius: int = 30):
        """
        Initialize a node in the graph with enhanced visual appearance.
        
        Args:
            node_id (str): Unique identifier for the node (e.g., 'P0', 'R1')
            node_type (str): Type of node ('process' or 'resource')
            position (Tuple[int, int]): (x, y) coordinates of the node
            radius (int): Radius of the node circle
        """
        self.id = node_id
        self.type = node_type
        self.position = position
        self.radius = radius
        self.selected = False
        self.color = (0, 200, 0) if node_type == 'process' else (200, 0, 0)  # Softer colors
        self.highlight_color = (0, 255, 0) if node_type == 'process' else (255, 0, 0)
        self.font = pygame.font.Font(None, 24)
        self.shadow_offset = 2
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the node on the screen with enhanced visual effects."""
        # Draw shadow
        shadow_pos = (self.position[0] + self.shadow_offset, 
                     self.position[1] + self.shadow_offset)
        pygame.draw.circle(screen, (100, 100, 100), shadow_pos, self.radius)
        
        # Draw main circle
        color = self.highlight_color if self.selected else self.color
        pygame.draw.circle(screen, color, self.position, self.radius)
        
        # Draw border
        pygame.draw.circle(screen, BLACK, self.position, self.radius, 2)
        
        # Draw node ID with shadow
        text = self.font.render(self.id, True, BLACK)
        text_rect = text.get_rect(center=self.position)
        screen.blit(text, text_rect)
        
        # Draw selection highlight
        if self.selected:
            pygame.draw.circle(screen, YELLOW, self.position, self.radius + 3, 2)
            
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the node was clicked."""
        distance = ((pos[0] - self.position[0]) ** 2 + 
                   (pos[1] - self.position[1]) ** 2) ** 0.5
        return distance <= self.radius
    
    def get_connections(self, edges: List['Edge']) -> List['Node']:
        """Get all nodes connected to this node."""
        connected_nodes = []
        for edge in edges:
            if edge.start == self:
                connected_nodes.append(edge.end)
            elif edge.end == self:
                connected_nodes.append(edge.start)
        return connected_nodes 