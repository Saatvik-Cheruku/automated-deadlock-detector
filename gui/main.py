import pygame
import sys
from .graph import Graph
from .node import Node
from .edge import Edge
from .ui_utils import Button, Panel, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WHITE, BLACK, DARK_GRAY

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deadlock Detection - No deadlock detected")

# Colors
BACKGROUND_COLOR = (245, 246, 250)  # Light gray background

# Create graph instance
graph = Graph()

# Create UI elements with adjusted position and size
check_button = Button(WIDTH - 180, 20, 140, 40, "Check Deadlock")  # Moved 20px more to the left
info_panel = Panel(10, 10, 250, 150, "Instructions")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                pos = pygame.mouse.get_pos()
                
                # Check if button was clicked
                if check_button.is_clicked(pos):
                    if graph.has_cycle():
                        pygame.display.set_caption("Deadlock Detection - DEADLOCK DETECTED!")
                        print("Deadlock detected!")
                    else:
                        pygame.display.set_caption("Deadlock Detection - No deadlock detected")
                        print("No deadlock detected.")
                
                # Add node or create edge
                else:
                    graph.handle_click(pos)
            
            elif event.button == 3:  # Right click
                pos = pygame.mouse.get_pos()
                graph.handle_right_click(pos)
        
        # Handle keyboard input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                graph.set_mode("process")
            elif event.key == pygame.K_2:
                graph.set_mode("resource")
        
        # Update button hover state
        if event.type == pygame.MOUSEMOTION:
            check_button.update(event.pos)
    
    # Draw everything
    # Draw background with gradient
    screen.fill(BACKGROUND_COLOR)
    
    # Draw a subtle grid pattern
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (230, 230, 230), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (230, 230, 230), (0, y), (WIDTH, y))
    
    # Draw the graph
    graph.draw(screen)
    
    # Draw UI elements
    check_button.draw(screen)
    info_panel.draw(screen)
    
    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit() 