import pygame
import sys
from gui.graph import Graph
from gui.node import Node
from gui.edge import Edge
from gui.ui_utils import Button, Panel

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deadlock Detection")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Create graph instance
graph = Graph()

# Create UI elements
check_button = Button(700, 50, 80, 30, "Check", GRAY)
info_panel = Panel(10, 10, 200, 100, "Instructions")

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
                        print("Deadlock detected!")
                    else:
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
    
    # Draw everything
    screen.fill(WHITE)
    graph.draw(screen)
    check_button.draw(screen)
    info_panel.draw(screen)
    
    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit() 