import pygame
from typing import Tuple

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Button dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = BLUE, 
                 hover_color: Tuple[int, int, int] = (0, 0, 200)):
        """
        Initialize a button.
        
        Args:
            x, y: Position of the button
            width, height: Dimensions of the button
            text: Button text
            color: Normal button color
            hover_color: Color when mouse hovers over button
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, 32)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen."""
        # Draw button background
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        
        # Draw button text
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_hovered(self) -> bool:
        """Check if the mouse is hovering over the button."""
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Check if the button was clicked."""
        return event.type == pygame.MOUSEBUTTONDOWN and \
               event.button == 1 and \
               self.is_hovered()

def create_buttons() -> Tuple[Button, Button]:
    """Create and return the check deadlock and reset buttons."""
    check_button = Button(
        BUTTON_MARGIN,
        SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "Check Deadlock"
    )
    
    reset_button = Button(
        BUTTON_MARGIN + BUTTON_WIDTH + BUTTON_MARGIN,
        SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "Reset"
    )
    
    return check_button, reset_button 