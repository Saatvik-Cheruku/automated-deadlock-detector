import pygame
from typing import Tuple

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

class Panel:
    def __init__(self, x: int, y: int, width: int, height: int, title: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.Font(None, 24)
        self.text_color = (0, 0, 0)
        self.bg_color = (240, 240, 240)
        self.border_color = (200, 200, 200)
        
    def draw(self, screen: pygame.Surface) -> None:
        # Draw panel background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw title
        title_surface = self.font.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(
            midtop=(self.rect.centerx, self.rect.top + 10)
        )
        screen.blit(title_surface, title_rect)
        
        # Draw instructions
        instructions = [
            "Press '1' for Process",
            "Press '2' for Resource",
            "Left-click to connect",
            "Right-click to delete"
        ]
        
        y_offset = 40
        for instruction in instructions:
            text_surface = self.font.render(instruction, True, self.text_color)
            text_rect = text_surface.get_rect(
                topleft=(self.rect.left + 10, self.rect.top + y_offset)
            )
            screen.blit(text_surface, text_rect)
            y_offset += 25 