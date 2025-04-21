import pygame
import random
import math
from typing import List, Tuple

class Star:
    def __init__(self, x: int, y: int, size: float, brightness: float):
        self.x = x
        self.y = y
        self.size = size
        self.brightness = brightness
        self.twinkle_speed = random.uniform(0.5, 2.0)
        self.twinkle_offset = random.uniform(0, 2 * math.pi)
        
    def update(self, dt: float):
        # Update twinkle effect
        self.twinkle_offset += self.twinkle_speed * dt
        self.current_brightness = self.brightness * (0.7 + 0.3 * math.sin(self.twinkle_offset))
        
    def draw(self, surface: pygame.Surface):
        # Draw star with glow effect
        color = (255, 255, 255, int(255 * self.current_brightness))
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        
        # Draw multiple circles for glow effect
        for i in range(3):
            alpha = int(100 * (1 - i/3) * self.current_brightness)
            pygame.draw.circle(glow_surf, (*color[:3], alpha), 
                             (self.size * 2, self.size * 2), 
                             self.size * (2 - i/2))
        
        surface.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))

class Planet:
    def __init__(self, x: int, y: int, size: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.orbit_radius = random.randint(100, 200)
        self.orbit_speed = random.uniform(0.2, 0.5)
        self.orbit_offset = random.uniform(0, 2 * math.pi)
        
    def update(self, dt: float):
        # Update orbit position
        self.orbit_offset += self.orbit_speed * dt
        self.x = self.orbit_radius * math.cos(self.orbit_offset)
        self.y = self.orbit_radius * math.sin(self.orbit_offset)
        
    def draw(self, surface: pygame.Surface):
        # Draw planet with glow effect
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        
        # Draw planet
        pygame.draw.circle(glow_surf, (*self.color, 255), 
                         (self.size * 2, self.size * 2), self.size)
        
        # Draw glow
        for i in range(3):
            alpha = int(100 * (1 - i/3))
            pygame.draw.circle(glow_surf, (*self.color, alpha), 
                             (self.size * 2, self.size * 2), 
                             self.size * (1.5 - i/3))
        
        surface.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))

class BackgroundSystem:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create stars
        self.stars: List[Star] = []
        for _ in range(200):  # Increased number of stars
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.uniform(0.5, 2.0)
            brightness = random.uniform(0.3, 1.0)
            self.stars.append(Star(x, y, size, brightness))
            
        # Create planets
        self.planets: List[Planet] = []
        planet_colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Purple
        ]
        for _ in range(3):  # Create 3 planets
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.uniform(10, 20)
            color = random.choice(planet_colors)
            self.planets.append(Planet(x, y, size, color))
            
        self.last_time = pygame.time.get_ticks()
        
    def update(self, dt: float):
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Clear surface with deep space color
        self.surface.fill((5, 5, 20, 255))  # Very dark blue
        
        # Update and draw stars
        for star in self.stars:
            star.update(dt)
            star.draw(self.surface)
            
        # Update and draw planets
        for planet in self.planets:
            planet.update(dt)
            planet.draw(self.surface)
            
    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, (0, 0)) 