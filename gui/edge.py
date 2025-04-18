import pygame
import math
from typing import List, Dict, Set, Optional, Tuple
from gui.node import Node
from gui.ui_utils import PRIMARY_COLOR, ACCENT_COLOR, create_gradient_surface

class Edge:
    def __init__(self, start: Node, end: Node):
        self.start = start
        self.end = end
        # Determine edge type based on node types
        if start.node_type == "process" and end.node_type == "resource":
            self.edge_type = "request"
            self.color = ACCENT_COLOR
        elif start.node_type == "resource" and end.node_type == "process":
            self.edge_type = "allocation"
            self.color = PRIMARY_COLOR
        else:
            self.edge_type = "invalid"
            self.color = (200, 200, 200)  # Gray for invalid edges
        
        self.arrow_size = 15
        self.glow_width = 6
        self.line_width = 2
        self.flow_time = 0
        self.flow_speed = 2
        self.selected = False
        self.in_deadlock = False
        
    def update(self, dt):
        self.flow_time += dt * self.flow_speed
        if self.flow_time > 1.0:
            self.flow_time -= 1.0
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the edge with enhanced visual effects."""
        # Calculate start and end points
        start_pos = (self.start.x, self.start.y)
        end_pos = (self.end.x, self.end.y)
        
        # Calculate direction vector
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return
            
        # Normalize direction vector
        dx, dy = dx/length, dy/length
        
        # Adjust start and end points to connect to node borders
        start_pos = (start_pos[0] + dx * self.start.radius,
                    start_pos[1] + dy * self.start.radius)
        end_pos = (end_pos[0] - dx * self.end.radius,
                  end_pos[1] - dy * self.end.radius)
        
        # Create surface for edge with glow effect
        padding = self.glow_width * 2
        surface_width = int(abs(end_pos[0] - start_pos[0])) + padding * 2
        surface_height = int(abs(end_pos[1] - start_pos[1])) + padding * 2
        
        if surface_width == 0 or surface_height == 0:
            return
            
        edge_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        
        # Translate coordinates to surface space
        local_start = (
            padding,
            padding if end_pos[1] >= start_pos[1] else surface_height - padding
        )
        local_end = (
            surface_width - padding,
            surface_height - padding if end_pos[1] >= start_pos[1] else padding
        )
        
        # Draw glow effect
        glow_color = (255, 100, 100) if self.in_deadlock else self.color
        for i in range(self.glow_width, 0, -1):
            alpha = int(100 * (i / self.glow_width))
            pygame.draw.line(edge_surface, (*glow_color, alpha),
                           local_start, local_end, i * 2)
        
        # Draw main line
        pygame.draw.line(edge_surface, (255, 255, 255),
                        local_start, local_end, self.line_width)
        
        # Draw flow particles
        num_particles = 5
        for i in range(num_particles):
            t = (i / num_particles + self.flow_time) % 1.0
            particle_pos = (
                local_start[0] + (local_end[0] - local_start[0]) * t,
                local_start[1] + (local_end[1] - local_start[1]) * t
            )
            
            # Draw particle glow
            particle_color = (255, 255, 255)
            for r in range(4, 0, -1):
                alpha = int(100 * (r / 4))
                pygame.draw.circle(edge_surface, (*particle_color, alpha),
                                 (int(particle_pos[0]), int(particle_pos[1])), r)
        
        # Draw arrow
        arrow_pos = (
            local_end[0] - dx * self.arrow_size,
            local_end[1] - dy * self.arrow_size
        )
        
        arrow_left = (
            arrow_pos[0] + dy * self.arrow_size * 0.5,
            arrow_pos[1] - dx * self.arrow_size * 0.5
        )
        
        arrow_right = (
            arrow_pos[0] - dy * self.arrow_size * 0.5,
            arrow_pos[1] + dx * self.arrow_size * 0.5
        )
        
        # Draw arrow glow
        for i in range(3):
            alpha = int(100 * ((3-i) / 3))
            pygame.draw.polygon(edge_surface, (*glow_color, alpha),
                              [local_end, arrow_left, arrow_right])
        
        # Draw solid arrow
        pygame.draw.polygon(edge_surface, (255, 255, 255),
                          [local_end, arrow_left, arrow_right])
        
        # Blit edge surface onto screen
        screen.blit(edge_surface,
                   (min(start_pos[0], end_pos[0]) - padding,
                    min(start_pos[1], end_pos[1]) - padding))
    
    def __eq__(self, other: 'Edge') -> bool:
        """Check if two edges are equal."""
        if not isinstance(other, Edge):
            return False
        return (self.start == other.start and self.end == other.end) or \
               (self.start == other.end and self.end == other.start)
    
    def __hash__(self) -> int:
        """Get the hash of the edge."""
        return hash((min(self.start, self.end), max(self.start, self.end))) 