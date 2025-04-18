import pygame
from typing import Tuple

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
PRIMARY_COLOR = (44, 62, 80)  # Dark blue
SECONDARY_COLOR = (52, 152, 219)  # Light blue
ACCENT_COLOR = (231, 76, 60)  # Red

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int] = PRIMARY_COLOR):
        self.text = text
        self.font = pygame.font.Font(None, 28)  # Increased font size
        
        # Calculate text size and adjust button width if needed
        text_surface = self.font.render(text, True, WHITE)
        text_width = text_surface.get_width() + 20  # Add padding
        self.rect = pygame.Rect(x, y, max(width, text_width), height)
        
        self.color = color
        self.hover_color = SECONDARY_COLOR
        self.text_color = WHITE
        self.is_hovered = False
        self.shadow_offset = 2
        
    def draw(self, screen: pygame.Surface) -> None:
        # Draw shadow first
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=5)
        
        # Draw main button background
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw border last
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update the button's hover state based on mouse position."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the button was clicked and update hover state."""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

class Panel:
    def __init__(self, x: int, y: int, width: int, height: int, title: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 28)
        self.text_color = BLACK
        self.bg_color = WHITE
        self.border_color = DARK_GRAY
        self.shadow_offset = 3
        self.padding = 10
        
    def draw(self, screen: pygame.Surface) -> None:
        # Draw shadow
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=10)
        
        # Draw panel background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=10)
        
        # Draw title
        title_surface = self.title_font.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(
            midtop=(self.rect.centerx, self.rect.top + self.padding)
        )
        screen.blit(title_surface, title_rect)
        
        # Draw instructions
        instructions = [
            "Press '1' for Process",
            "Press '2' for Resource",
            "Left-click to connect",
            "Right-click to delete"
        ]
        
        y_offset = title_rect.bottom + self.padding
        for instruction in instructions:
            text_surface = self.font.render(instruction, True, self.text_color)
            text_rect = text_surface.get_rect(
                topleft=(self.rect.left + self.padding, y_offset)
            )
            screen.blit(text_surface, text_rect)
            y_offset += 30 