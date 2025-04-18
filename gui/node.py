import pygame
from typing import Tuple, List

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Node:
    def __init__(self, position: Tuple[int, int], node_type: str):
        """
        Initialize a node with enhanced visual appearance.
        
        Args:
            position (tuple): (x, y) coordinates
            node_type (str): 'process' or 'resource'
        """
        self.position = position
        self.type = node_type
        self.radius = 20
        self.color = GREEN if node_type == 'process' else RED
        self.selected = False
        self.highlight_color = BLUE
        self.border_width = 3
        self.shadow_offset = 2
        self.in_deadlock = False
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the node on the screen with enhanced visual effects."""
        x, y = self.position
        
        # Draw shadow
        shadow_pos = (x + self.shadow_offset, y + self.shadow_offset)
        pygame.draw.circle(screen, (100, 100, 100), shadow_pos, self.radius)
        
        # Draw main circle
        if self.in_deadlock:
            # Draw warning glow for deadlocked nodes
            pygame.draw.circle(screen, YELLOW, self.position, self.radius + 5)
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            border_color = YELLOW
        else:
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            border_color = self.highlight_color if self.selected else BLACK
        
        # Draw border
        pygame.draw.circle(screen, border_color, self.position, self.radius, self.border_width)
        
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

    def __hash__(self) -> int:
        """Make Node objects hashable."""
        return hash((self.position, self.type))

    def get_connections(self, edges: List['Edge']) -> List['Node']:
        """Get all nodes connected to this node."""
        connected_nodes = []
        for edge in edges:
            if edge.start == self:
                connected_nodes.append(edge.end)
            elif edge.end == self:
                connected_nodes.append(edge.start)
        return connected_nodes 