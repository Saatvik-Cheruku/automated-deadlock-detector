import pygame
import math
from typing import Tuple, List, Dict, Set, Optional
from gui.ui_utils import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, SUCCESS_COLOR, WARNING_COLOR, create_gradient_surface

class Node:
    def __init__(self, x: int, y: int, node_type: str = "process"):
        """
        Initialize a node with enhanced visual appearance.
        
        Args:
            x (int): x coordinate
            y (int): y coordinate
            node_type (str): 'process' or 'resource'
        """
        self.x = x
        self.y = y
        self.radius = 20
        self.node_type = node_type
        self.color = (255, 100, 100) if node_type == "process" else (100, 100, 255)
        self.glow_radius = self.radius * 1.5
        self.animation_time = 0
        self.selected = False
        self.hover = False
        self.highlight_color = PRIMARY_COLOR
        self.border_width = 3
        self.shadow_offset = 3
        self.in_deadlock = False
        self.glow_surface = None
        self.update_glow_surface()
        
    def update(self, dt: float) -> None:
        """Update node animation"""
        self.animation_time += dt
        if self.animation_time >= 2 * math.pi:
            self.animation_time = 0
        self.update_glow_surface()
        
    def update_glow_surface(self):
        # Create glow surface if not exists
        if self.glow_surface is None:
            size = self.radius * 4
            self.glow_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
        self.glow_surface.fill((0, 0, 0, 0))
        
        # Base glow color
        glow_color = self.color
        size = self.radius * 4
        center = (size, size)
        
        # Draw multiple circles with decreasing alpha for glow effect
        for r in range(size, 0, -2):
            alpha = int(50 * (r/size))
            if self.selected:
                # Pulsing glow for selected state
                alpha = int(alpha * (1 + 0.5 * math.sin(self.animation_time * 4)))
            elif self.hover:
                # Enhanced glow for hover state
                alpha = int(alpha * 1.5)
            pygame.draw.circle(self.glow_surface, (*glow_color, alpha), center, r)
            
        # Add rotating highlight for selected state
        if self.selected:
            highlight_points = []
            segments = 30
            inner_radius = self.radius * 2
            outer_radius = self.radius * 2.5
            
            for i in range(segments):
                angle = self.animation_time + (i * 2 * math.pi / segments)
                inner_point = (
                    center[0] + math.cos(angle) * inner_radius,
                    center[1] + math.sin(angle) * inner_radius
                )
                outer_point = (
                    center[0] + math.cos(angle) * outer_radius,
                    center[1] + math.sin(angle) * outer_radius
                )
                highlight_points.append(inner_point)
                highlight_points.append(outer_point)
                
            if len(highlight_points) >= 4:
                pygame.draw.polygon(self.glow_surface, (*glow_color, 30), highlight_points)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the node on the screen with enhanced visual effects."""
        # Draw glow effect
        glow_pos = (
            int(self.x - self.glow_surface.get_width()//2),
            int(self.y - self.glow_surface.get_height()//2)
        )
        screen.blit(self.glow_surface, glow_pos)
        
        # Draw main circle with gradient
        gradient_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        for r in range(self.radius, 0, -1):
            progress = r / self.radius
            color = [int(c * (0.8 + 0.2 * progress)) for c in self.color]
            pygame.draw.circle(gradient_surface, (*color, 255), 
                             (self.radius, self.radius), r)
        
        # Add highlight
        highlight_radius = int(self.radius * 0.7)
        highlight_pos = (int(self.radius * 0.7), int(self.radius * 0.7))
        for r in range(highlight_radius, 0, -1):
            progress = r / highlight_radius
            alpha = int(150 * progress)
            pygame.draw.circle(gradient_surface, (255, 255, 255, alpha),
                             highlight_pos, r)
        
        # Draw node surface
        node_pos = (
            int(self.x - self.radius),
            int(self.y - self.radius)
        )
        screen.blit(gradient_surface, node_pos)
        
        # Draw node type indicator
        if self.node_type == "process":
            # Draw P with gradient
            font = pygame.font.Font(None, int(self.radius * 1.5))
            text = font.render("P", True, (255, 255, 255))
            text_pos = (
                self.x - text.get_width()//2,
                self.y - text.get_height()//2
            )
            screen.blit(text, text_pos)
        else:
            # Draw resource diamond
            diamond_size = self.radius * 0.6
            diamond_points = [
                (self.x, self.y - diamond_size),
                (self.x + diamond_size, self.y),
                (self.x, self.y + diamond_size),
                (self.x - diamond_size, self.y)
            ]
            pygame.draw.polygon(gradient_surface, (255, 255, 255, 230), diamond_points)
        
        # Draw selection/hover indicator
        if self.selected or self.hover:
            ring_radius = self.radius * 1.2
            ring_width = 2
            ring_color = (255, 255, 255, int(200 * (0.5 + 0.5 * math.sin(self.animation_time * 4))))
            pygame.draw.circle(gradient_surface, ring_color, (self.radius, self.radius), ring_radius, ring_width)
        
        # Draw shadow with gradient effect
        shadow_pos = (self.x + self.shadow_offset, self.y + self.shadow_offset)
        pygame.draw.circle(gradient_surface, (200, 200, 200), shadow_pos, self.radius)
        
        # Draw main circle with glow effect if in deadlock
        if self.in_deadlock:
            # Draw warning glow for deadlocked nodes
            glow_surface = pygame.Surface((self.radius * 2 + self.glow_radius * 2,) * 2, pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*WARNING_COLOR, 100), (self.radius + self.glow_radius,) * 2, self.radius + self.glow_radius)
            gradient_surface.blit(glow_surface, (self.x - self.radius - self.glow_radius, self.y - self.radius - self.glow_radius))
            pygame.draw.circle(gradient_surface, self.color, (self.x, self.y), self.radius)
            border_color = WARNING_COLOR
        else:
            border_color = self.highlight_color if self.selected or self.hover else self.color
        
        # Draw border
        pygame.draw.circle(gradient_surface, border_color, (self.radius, self.radius), self.radius, self.border_width)
        
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside the node."""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2) <= self.radius
        
    def __eq__(self, other: 'Node') -> bool:
        """Check if two nodes are equal."""
        return isinstance(other, Node) and self.x == other.x and self.y == other.y
        
    def __hash__(self) -> int:
        """Get the hash of the node."""
        return hash((self.x, self.y))
        
    def get_connections(self, edges: List['Edge']) -> List['Node']:
        """Get all nodes connected to this node."""
        connected = []
        for edge in edges:
            if edge.start == self:
                connected.append(edge.end)
            elif edge.end == self:
                connected.append(edge.start)
        return connected 