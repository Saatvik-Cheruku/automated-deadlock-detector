import pygame
import sys
from .graph import Graph
from .utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN,
    create_buttons, Button
)

class DeadlockDetector:
    def __init__(self):
        """Initialize the deadlock detector application."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Deadlock Detector")
        
        self.clock = pygame.time.Clock()
        self.graph = Graph()
        self.check_button, self.reset_button = create_buttons()
        
        # State variables
        self.selected_node = None
        self.status_message = ""
        self.status_color = BLACK
        self.font = pygame.font.Font(None, 36)
        
    def handle_events(self) -> bool:
        """Handle pygame events and return False if the application should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(event.pos)
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Create process node
                    self.create_node('process', event.pos)
                elif event.key == pygame.K_2:  # Create resource node
                    self.create_node('resource', event.pos)
                    
        return True
        
    def handle_left_click(self, pos: tuple) -> None:
        """Handle left mouse button clicks."""
        # Check if buttons were clicked
        if self.check_button.is_clicked(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})):
            self.check_deadlock()
            return
        elif self.reset_button.is_clicked(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})):
            self.reset_graph()
            return
            
        # Handle node selection and edge creation
        clicked_node = self.graph.get_node_at_position(pos)
        
        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
                clicked_node.selected = True
            else:
                if self.selected_node != clicked_node:
                    # Create edge between selected nodes
                    if self.selected_node.type == 'process' and clicked_node.type == 'resource':
                        edge_type = 'request'
                    elif self.selected_node.type == 'resource' and clicked_node.type == 'process':
                        edge_type = 'allocation'
                    else:
                        edge_type = 'request'  # Default to request
                        
                    self.graph.add_edge(self.selected_node, clicked_node, edge_type)
                    
                self.selected_node.selected = False
                self.selected_node = None
        else:
            # Clicked on empty space, deselect node
            if self.selected_node:
                self.selected_node.selected = False
                self.selected_node = None
                
    def handle_right_click(self, pos: tuple) -> None:
        """Handle right mouse button clicks."""
        clicked_node = self.graph.get_node_at_position(pos)
        if clicked_node:
            self.graph.remove_node(clicked_node)
            
    def create_node(self, node_type: str, pos: tuple) -> None:
        """Create a new node at the specified position."""
        self.graph.add_node(node_type, pos)
        
    def check_deadlock(self) -> None:
        """Check for deadlock and update the status message."""
        if self.graph.detect_deadlock():
            self.status_message = "⚠️ DEADLOCK DETECTED!"
            self.status_color = RED
        else:
            self.status_message = "✅ No Deadlock Detected"
            self.status_color = GREEN
            
    def reset_graph(self) -> None:
        """Reset the graph and clear status message."""
        self.graph.reset()
        self.selected_node = None
        self.status_message = ""
        self.status_color = BLACK
        
    def draw(self) -> None:
        """Draw all elements on the screen."""
        self.screen.fill(WHITE)
        
        # Draw status message
        if self.status_message:
            text_surface = self.font.render(self.status_message, True, self.status_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(text_surface, text_rect)
            
        # Draw graph
        self.graph.draw(self.screen)
        
        # Draw buttons
        self.check_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        
        pygame.display.flip()
        
    def run(self) -> None:
        """Run the main application loop."""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DeadlockDetector()
    app.run() 