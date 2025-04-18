import pygame
from typing import Tuple
from .utils import BLACK

class Edge:
    def __init__(self, start: 'Node', end: 'Node', edge_type: str):
        """
        Initialize an edge in the graph with enhanced visual appearance.
        
        Args:
            start (Node): Starting node
            end (Node): Ending node
            edge_type (str): Type of edge ('request' or 'allocation')
        """
        self.start = start
        self.end = end
        self.type = edge_type
        self.color = (0, 0, 200) if edge_type == 'request' else (200, 100, 0)  # Softer colors
        self.highlight_color = (0, 0, 255) if edge_type == 'request' else (255, 165, 0)
        self.width = 2
        self.arrow_length = 15
        self.arrow_angle = 30
        self.shadow_offset = 1
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the edge on the screen with enhanced visual effects."""
        # Calculate arrow points
        start_pos = self.start.position
        end_pos = self.end.position
        
        # Calculate direction vector
        direction = pygame.math.Vector2(end_pos[0] - start_pos[0], 
                                      end_pos[1] - start_pos[1])
        if direction.length() == 0:
            return
            
        # Normalize direction
        direction = direction.normalize()
        
        # Calculate perpendicular vector for offset
        perp = pygame.math.Vector2(-direction.y, direction.x)
        
        # Draw shadow
        shadow_start = (start_pos[0] + self.shadow_offset, 
                       start_pos[1] + self.shadow_offset)
        shadow_end = (end_pos[0] + self.shadow_offset, 
                     end_pos[1] + self.shadow_offset)
        pygame.draw.line(screen, (100, 100, 100), shadow_start, shadow_end, self.width)
        
        # Draw main line
        pygame.draw.line(screen, self.color, start_pos, end_pos, self.width)
        
        # Calculate arrow points
        arrow_base = (end_pos[0] - direction.x * self.arrow_length,
                     end_pos[1] - direction.y * self.arrow_length)
        
        arrow_point1 = (
            arrow_base[0] - direction.x * self.arrow_length * 0.5 + perp.x * self.arrow_length * 0.5,
            arrow_base[1] - direction.y * self.arrow_length * 0.5 + perp.y * self.arrow_length * 0.5
        )
        
        arrow_point2 = (
            arrow_base[0] - direction.x * self.arrow_length * 0.5 - perp.x * self.arrow_length * 0.5,
            arrow_base[1] - direction.y * self.arrow_length * 0.5 - perp.y * self.arrow_length * 0.5
        )
        
        # Draw arrow head
        pygame.draw.polygon(screen, self.color, [end_pos, arrow_point1, arrow_point2])
        
    def __eq__(self, other: 'Edge') -> bool:
        """Check if two edges are equal."""
        return (self.start == other.start and self.end == other.end) or \
               (self.start == other.end and self.end == other.start) 