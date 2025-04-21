import pygame
from typing import Tuple, List, Optional, Callable
import math
import colorsys
import time

# Modern color palette with professional tones
PRIMARY_COLOR = (41, 128, 185)      # Professional blue
SECONDARY_COLOR = (52, 152, 219)    # Light blue
ACCENT_COLOR = (231, 76, 60)        # Clean red
SUCCESS_COLOR = (46, 204, 113)      # Emerald green
WARNING_COLOR = (241, 196, 15)      # Golden yellow
PANEL_BG = (44, 62, 80)            # Dark blue-gray
GRID_COLOR = (52, 73, 94)          # Lighter blue-gray
TEXT_COLOR = (236, 240, 241)       # Almost white
SHADOW_COLOR = (0, 0, 0, 40)

def pulse_color(base_color: Tuple[int, int, int], intensity: float) -> Tuple[int, int, int]:
    """Create a pulsing color effect"""
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(base_color[0]/255, base_color[1]/255, base_color[2]/255)
    # Adjust value (brightness) based on intensity
    v = min(1.0, v * (1.0 + intensity * 0.3))
    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def create_gradient_surface(width: int, height: int, 
                          color_start: Tuple[int, ...], 
                          color_end: Tuple[int, ...]) -> pygame.Surface:
    """Create a surface with a vertical gradient between two colors."""
    surface = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
    
    for y in range(int(height)):
        t = y / height
        color = tuple(int(a + (b - a) * t) for a, b in zip(color_start, color_end))
        pygame.draw.line(surface, color, (0, y), (width, y))
    
    return surface

def get_pulse_color(base_color: Tuple[int, int, int], 
                   time: float, 
                   pulse_speed: float = 2.0,
                   pulse_range: float = 0.2) -> Tuple[int, int, int]:
    """Get a color that pulses in brightness."""
    pulse = 1.0 + math.sin(time * pulse_speed) * pulse_range
    return tuple(min(255, int(c * pulse)) for c in base_color)

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 28)
        self.is_active = False
        self.hover = False
        self.clicked = False
        self.animation_time = 0.0
        self.rect = pygame.Rect(x, y, width, height)
        self.result_color = None
        self.result_animation_start = 0
        self.result_animation_duration = 1.0  # 1 second
        self.border_radius = 20  # Increased border radius
        
    def animate_result(self, success):
        """Start animation for success/failure"""
        self.result_color = SUCCESS_COLOR if success else ACCENT_COLOR
        self.result_animation_start = time.time()
        
    def update(self, mouse_pos):
        """Update button state"""
        self.hover = self.rect.collidepoint(mouse_pos)
        self.animation_time += 0.1
        
        # Update result animation
        if self.result_color:
            elapsed = time.time() - self.result_animation_start
            if elapsed > self.result_animation_duration:
                self.result_color = None
        
    def is_clicked(self, pos):
        """Check if button was clicked and handle the click"""
        if self.rect.collidepoint(pos):
            self.clicked = True
            if self.callback:
                self.callback()
            return True
        return False
        
    def draw(self, screen):
        # Create button surface with transparency
        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create gradient background
        if self.is_active:
            gradient = create_gradient_surface(self.width, self.height, 
                                            (41, 128, 185), (52, 152, 219))
        else:
            gradient = create_gradient_surface(self.width, self.height, 
                                            (44, 62, 80), (52, 73, 94))
        button_surface.blit(gradient, (0, 0))
        
        # Draw rounded rectangle
        pygame.draw.rect(button_surface, (*PANEL_BG, 230),
                        (0, 0, self.width, self.height),
                        border_radius=self.border_radius)
        
        # Add hover effect
        if self.hover:
            hover_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            hover_surface.fill((255, 255, 255, 30))
            pygame.draw.rect(hover_surface, (255, 255, 255, 30),
                           (0, 0, self.width, self.height),
                           border_radius=self.border_radius)
            button_surface.blit(hover_surface, (0, 0))
            
        # Add click effect
        if self.clicked:
            click_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            click_surface.fill((0, 0, 0, 50))
            pygame.draw.rect(click_surface, (0, 0, 0, 50),
                           (0, 0, self.width, self.height),
                           border_radius=self.border_radius)
            button_surface.blit(click_surface, (0, 0))
            self.clicked = False
            
        # Add result animation
        if self.result_color:
            elapsed = time.time() - self.result_animation_start
            progress = min(1.0, elapsed / self.result_animation_duration)
            alpha = int(150 * (1 - progress))
            result_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            result_surface.fill((*self.result_color, alpha))
            pygame.draw.rect(result_surface, (*self.result_color, alpha),
                           (0, 0, self.width, self.height),
                           border_radius=self.border_radius)
            button_surface.blit(result_surface, (0, 0))
        
        # Draw text
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.width//2, self.height//2))
        
        # Add text shadow
        shadow_surface = self.font.render(self.text, True, (0, 0, 0, 100))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, 
                                                    text_rect.centery + 1))
        button_surface.blit(shadow_surface, shadow_rect)
        button_surface.blit(text_surface, text_rect)
        
        # Draw button with shadow
        shadow = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 40))
        pygame.draw.rect(shadow, (0, 0, 0, 40),
                        (0, 0, self.width + 4, self.height + 4),
                        border_radius=self.border_radius + 2)
        screen.blit(shadow, (self.x - 2, self.y - 2))
        screen.blit(button_surface, (self.x, self.y))

class Panel:
    def __init__(self, x, y, width, height, title, instructions):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.title = title
        self.instructions = instructions
        self.font = pygame.font.Font(None, 24)  # Slightly smaller font
        self.title_font = pygame.font.Font(None, 32)  # Smaller title font
        self.padding = 20
        self.line_spacing = 12
        self.animation_time = 0.0
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 20
        
        # Calculate required height based on content
        self.calculate_dimensions()
        
    def calculate_dimensions(self):
        """Calculate the required height based on content"""
        total_height = self.padding * 1.5  # Start with top padding
        
        # Add title height
        title_surface = self.title_font.render(self.title, True, TEXT_COLOR)
        total_height += title_surface.get_height() + 15  # Less space after title
        
        # Calculate height needed for instructions
        for line in self.instructions:
            text_surface = self.font.render(line, True, TEXT_COLOR)
            total_height += text_surface.get_height() + self.line_spacing
            
        # Add bottom padding
        total_height += self.padding
        
        # Calculate maximum scroll
        self.max_scroll = max(0, total_height - self.height)
        
    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, 
                                          self.scroll_offset - event.y * self.scroll_speed))
            
    def draw(self, screen):
        self.animation_time += 0.02
        
        # Create panel surface with transparency
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create a more sophisticated gradient background
        base_color = (*PANEL_BG, 230)  # More transparent
        highlight_color = tuple(min(255, c + 10) for c in PANEL_BG) + (230,)
        shadow_color = tuple(max(0, c - 10) for c in PANEL_BG) + (230,)
        
        # Draw main gradient
        gradient = create_gradient_surface(self.width, self.height,
                                        highlight_color,
                                        shadow_color)
        panel_surface.blit(gradient, (0, 0))
        
        # Draw rounded rectangle with glass effect
        pygame.draw.rect(panel_surface, (*PANEL_BG, 230),
                        (0, 0, self.width, self.height),
                        border_radius=15)  # Smaller border radius
        
        # Add glass reflection effect at the top
        glass_height = self.height // 4
        glass_surface = pygame.Surface((self.width, glass_height), pygame.SRCALPHA)
        for i in range(glass_height):
            progress = i / glass_height
            alpha = int(15 * (1 - progress))  # Reduced reflection intensity
            pygame.draw.line(glass_surface, (255, 255, 255, alpha),
                           (0, i), (self.width, i))
        panel_surface.blit(glass_surface, (0, 0))
        
        # Draw title with subtle glow
        title_surface = self.title_font.render(self.title, True, TEXT_COLOR)
        title_rect = title_surface.get_rect(
            midtop=(self.width // 2, self.padding)
        )
        
        # Draw title shadow and text
        shadow_surface = self.title_font.render(self.title, True, (0, 0, 0, 50))
        shadow_rect = shadow_surface.get_rect(
            midtop=(title_rect.centerx + 1, title_rect.top + 1)
        )
        panel_surface.blit(shadow_surface, shadow_rect)
        panel_surface.blit(title_surface, title_rect)
        
        # Create a clipping surface for instructions
        clip_surface = pygame.Surface((self.width - self.padding * 2, 
                                     self.height - title_rect.bottom - self.padding),
                                    pygame.SRCALPHA)
        
        # Draw instructions with scroll offset
        y = 0
        for line in self.instructions:
            text_surface = self.font.render(line, True, TEXT_COLOR)
            clip_surface.blit(text_surface, (0, y - self.scroll_offset))
            y += text_surface.get_height() + self.line_spacing
            
        # Draw the clipped instructions
        panel_surface.blit(clip_surface, 
                         (self.padding, title_rect.bottom + self.padding))
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            # Draw scroll bar background
            scroll_height = (self.height - title_rect.bottom - self.padding * 2)
            scroll_pos = (self.scroll_offset / self.max_scroll) * scroll_height
            pygame.draw.rect(panel_surface, (100, 100, 100, 100),
                           (self.width - 10, title_rect.bottom + self.padding,
                            5, scroll_height))
            # Draw scroll thumb
            pygame.draw.rect(panel_surface, (200, 200, 200, 200),
                           (self.width - 10, title_rect.bottom + self.padding + scroll_pos,
                            5, 20))
        
        # Add subtle outer glow
        glow_width = self.width + 10
        glow_height = self.height + 10
        glow_surface = pygame.Surface((int(glow_width), int(glow_height)), pygame.SRCALPHA)
        for i in range(3):  # Fewer glow layers
            alpha = int(15 - i * 5)  # Reduced glow intensity
            pygame.draw.rect(glow_surface, (*PRIMARY_COLOR, alpha),
                           (i, i, int(glow_width - i*2), int(glow_height - i*2)),
                           border_radius=15)
        
        # Apply panel to screen with shadow and glow
        screen.blit(glow_surface, (self.x - 5, self.y - 5))
        screen.blit(panel_surface, (self.x, self.y))
        
    def contains_point(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)

class Popup:
    def __init__(self, message, success, duration=2.0):
        self.message = message
        self.success = success
        self.duration = duration
        self.time_remaining = duration
        self.font = pygame.font.Font(None, 28)  # Slightly smaller font
        self.padding = 20
        self.animation_progress = 0.0
        self.fade_progress = 1.0
        
    def update(self, dt):
        self.time_remaining -= dt
        self.animation_progress = min(1.0, self.animation_progress + dt * 3)  # Faster animation
        if self.time_remaining < 0.5:
            self.fade_progress = max(0.0, self.time_remaining * 2)
        return self.time_remaining <= 0
        
    def draw(self, screen):
        # Calculate dimensions
        text_surface = self.font.render(self.message, True, TEXT_COLOR)
        width = max(300, text_surface.get_width() + self.padding * 2)  # Smaller minimum width
        height = text_surface.get_height() + self.padding * 2
        
        # Calculate position with smooth animation
        x = (screen.get_width() - width) // 2
        base_y = screen.get_height() // 4
        scale = 1.0 + math.sin(self.animation_progress * math.pi) * 0.05  # Reduced bounce
        y = base_y - (1 - scale) * height // 2
        
        # Create popup surface
        popup_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw background with full color
        color = SUCCESS_COLOR if self.success else ACCENT_COLOR
        darker_color = tuple(max(0, c - 30) for c in color)  # Less contrast
        
        # Create gradient background
        gradient = create_gradient_surface(width, height,
                                        (*color, int(230 * self.fade_progress)),  # More transparent
                                        (*darker_color, int(230 * self.fade_progress)))
        popup_surface.blit(gradient, (0, 0))
        
        # Add subtle glass effect at the top
        glass_highlight = create_gradient_surface(width, height // 3,
                                                (255, 255, 255, 20),  # Reduced highlight
                                                (255, 255, 255, 0))
        popup_surface.blit(glass_highlight, (0, 0))
        
        # Draw rounded rectangle border
        pygame.draw.rect(popup_surface, (*color, int(230 * self.fade_progress)),
                        (0, 0, width, height), border_radius=12)  # Smaller border radius
        
        # Draw message with shadow
        shadow_surface = self.font.render(self.message, True, (0, 0, 0, int(50 * self.fade_progress)))
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        
        # Draw text on popup surface
        popup_surface.blit(shadow_surface, 
                          (text_rect.x + 1, text_rect.y + 1))
        popup_surface.blit(text_surface, text_rect)
        
        # Draw progress bar
        progress = self.time_remaining / self.duration
        bar_height = 4  # Thinner progress bar
        bar_width = int(width * progress)
        
        # Draw bar background
        pygame.draw.rect(popup_surface, (*darker_color, int(80 * self.fade_progress)),
                        (0, height - bar_height, width, bar_height))
        
        # Draw progress
        pygame.draw.rect(popup_surface, (255, 255, 255, int(150 * self.fade_progress)),
                        (0, height - bar_height, bar_width, bar_height))
        
        # Apply shadow
        shadow_surface = pygame.Surface((width + 8, height + 8), pygame.SRCALPHA)
        for i in range(3):  # Fewer shadow layers
            alpha = int((30 - i * 10) * self.fade_progress)
            pygame.draw.rect(shadow_surface, (0, 0, 0, alpha),
                           (i, i, width + 8 - i*2, height + 8 - i*2),
                           border_radius=12)
        
        # Draw everything to screen
        screen.blit(shadow_surface, (x - 4, y - 4))
        screen.blit(popup_surface, (x, y))

    def handle_mouse_click(self, pos: Tuple[int, int], button: int):
        """Handle mouse click"""
        # Check mode button clicks
        for btn in this.mode_buttons.values():
            if btn.is_clicked(pos):
                this.set_mode(btn.text.lower().split()[0])
                return
                
        # Check action button clicks
        if this.check_deadlock_button.is_clicked(pos):
            this.check_deadlock()
            return
        if this.clear_graph_button.is_clicked(pos):
            this.clear_graph()
            return
            
        # Check edge type button clicks
        if this.request_edge_button.is_clicked(pos):
            this.set_edge_type("request")
            return
        if this.allocation_edge_button.is_clicked(pos):
            this.set_edge_type("allocation")
            return 