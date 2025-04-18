import pygame
from typing import Tuple, List

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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
        self.color = GREEN if node_type == 'process' else RED
        self.highlight_color = BLUE
        self.font = pygame.font.Font(None, 24)
        self.shadow_offset = 2
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the node on the screen with enhanced visual effects."""
        # Draw shadow
        shadow_pos = (self.position[0] + self.shadow_offset, 
                     self.position[1] + self.shadow_offset)
        pygame.draw.circle(screen, (100, 100, 100), shadow_pos, self.radius)
        
        # Draw main circle
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        
        # Draw border
        border_color = self.highlight_color if self.selected else BLACK
        pygame.draw.circle(screen, border_color, self.position, self.radius, 3)
        
        # Draw node ID with shadow
        text = self.font.render(self.id, True, BLACK)
        text_rect = text.get_rect(center=self.position)
        screen.blit(text, text_rect)
        
        # Draw selection highlight
        if self.selected:
            pygame.draw.circle(screen, WHITE, self.position, self.radius + 3, 2)
            
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

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside the node."""
        x, y = point
        node_x, node_y = self.position
        distance = ((x - node_x) ** 2 + (y - node_y) ** 2) ** 0.5
        return distance <= self.radius
        
    def __eq__(self, other: 'Node') -> bool:
        """Check if two nodes are equal."""
        if not isinstance(other, Node):
            return False
        return self.position == other.position and self.type == other.type 