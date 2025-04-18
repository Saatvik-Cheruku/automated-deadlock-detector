import pygame
import random
import math
from typing import List, Tuple

class BackgroundSystem:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.time = 0
        
        # Create gradient surface
        self.gradient_surface = self.create_gradient_surface()

    def create_gradient_surface(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create a subtle gradient from dark blue to slightly lighter blue
        for y in range(self.height):
            # Calculate gradient color
            progress = y / self.height
            r = int(2 + progress * 5)  # Very subtle red component
            g = int(3 + progress * 8)  # Very subtle green component
            b = int(12 + progress * 15)  # Blue component
            color = (r, g, b, 255)
            
            # Draw horizontal line with current color
            pygame.draw.line(surface, color, (0, y), (self.width, y))
        
        return surface

    def update(self, dt: float):
        self.time += dt

    def draw(self, screen: pygame.Surface):
        # Draw the gradient background
        screen.blit(self.gradient_surface, (0, 0))
        
        # Add a very subtle grid pattern
        grid_color = (10, 15, 30, 30)  # Very dark blue, mostly transparent
        grid_spacing = 50
        
        # Draw vertical lines
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(screen, grid_color, (x, 0), (x, self.height))
        
        # Draw horizontal lines
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(screen, grid_color, (0, y), (self.width, y)) 