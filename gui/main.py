import pygame
import sys
import os
import math
from typing import List, Optional, Tuple

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from gui.background_system import BackgroundSystem
from gui.ui_utils import Panel, Button, Popup, PANEL_BG, create_gradient_surface, GRID_COLOR, SUCCESS_COLOR, ACCENT_COLOR
from gui.deadlock_detector import DeadlockDetector
from gui.process import Process, Resource
from gui.graph import Graph
from gui.node import Node
from gui.edge import Edge

# Define colors for different node types
PROCESS_COLORS = [
    (50, 205, 50),    # Lime Green
    (147, 112, 219),  # Purple
    (255, 165, 0)     # Orange
]

class DeadlockSimulator:
    def __init__(self):
        pygame.init()
        
        # Get screen info for responsive sizing
        screen_info = pygame.display.Info()
        self.width = min(int(screen_info.current_w * 0.8), 1280)
        self.height = min(int(screen_info.current_h * 0.8), 800)
        
        # Center the window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        # Create window with hardware acceleration
        self.screen = pygame.display.set_mode((self.width, self.height), 
                                            pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Deadlock Detection Simulator 🎮")
        
        # Initialize background system
        self.background = BackgroundSystem(self.width, self.height)
        
        # Initialize state
        self.selected_node = None
        self.dragging = False
        self.clock = pygame.time.Clock()
        self.animation_time = 0
        self.next_color_index = 0
        self.current_mode = "process"  # Default mode
        self.edge_start = None  # For edge creation
        self.edge_type = "request"  # Default edge type
        
        # Initialize deadlock detector
        self.detector = DeadlockDetector()
        
        # Create instruction panel
        self.setup_ui()
        
        self.popup = None
        self.running = True
        
    def setup_ui(self):
        # Create instruction panel on the left
        panel_width = 300
        self.panel = Panel(
            20, 20,
            panel_width, 250,  # Increased height for more instructions
            "Instructions",
            [
                "Node Creation:",
                "• Process Mode (P): Create process nodes",
                "• Resource Mode (R): Create resource nodes",
                "",
                "Edge Creation:",
                "• Edge Mode: Create relationships",
                "• Click first node then second",
                "• Request: Process → Resource",
                "• Allocation: Resource → Process",
                "",
                "Other:",
                "• Right-click to delete nodes",
                "• Check Deadlock to analyze"
            ]
        )
        
        # Create buttons
        button_width = 150
        button_height = 40
        button_spacing = 20
        
        # Mode selector buttons
        self.process_mode_button = Button(
            self.width - button_width * 3 - button_spacing * 2 - 20, 20,
            button_width, button_height,
            "Process Mode (P)",
            lambda: self.set_mode("process")
        )
        
        self.resource_mode_button = Button(
            self.width - button_width * 2 - button_spacing - 20, 20,
            button_width, button_height,
            "Resource Mode (R)",
            lambda: self.set_mode("resource")
        )
        
        self.edge_mode_button = Button(
            self.width - button_width - 20, 20,
            button_width, button_height,
            "Edge Mode (E)",
            lambda: self.set_mode("edge")
        )
        
        # Edge type selector buttons
        self.request_edge_button = Button(
            self.width - button_width * 2 - button_spacing - 20, 20 + button_height + button_spacing,
            button_width, button_height,
            "Request Edge",
            lambda: self.set_edge_type("request")
        )
        
        self.allocation_edge_button = Button(
            self.width - button_width - 20, 20 + button_height + button_spacing,
            button_width, button_height,
            "Allocation Edge",
            lambda: self.set_edge_type("allocation")
        )
        
        # Check deadlock button
        self.check_button = Button(
            self.width - button_width - 20, 20 + (button_height + button_spacing) * 2,
            button_width, button_height,
            "Check Deadlock",
            self.check_deadlock
        )
        
    def set_mode(self, mode: str):
        """Set the current node creation mode"""
        self.current_mode = mode
        # Update button colors
        self.process_mode_button.is_active = (mode == "process")
        self.resource_mode_button.is_active = (mode == "resource")
        self.edge_mode_button.is_active = (mode == "edge")
        
    def get_next_process_color(self):
        color = PROCESS_COLORS[self.next_color_index]
        self.next_color_index = (self.next_color_index + 1) % len(PROCESS_COLORS)
        return color
        
    def add_process(self, pos):
        """Add a process at the given position"""
        process = self.detector.add_process(pos)
        process.color = self.get_next_process_color()
        return process
        
    def add_resource(self, pos):
        """Add a resource at the given position"""
        return self.detector.add_resource(pos)
        
    def check_deadlock(self):
        """Check for deadlocks and display result"""
        has_deadlock, deadlocked = self.detector.detect_deadlock()
        if has_deadlock:
            self.popup = Popup("Deadlock Detected!", False)
            self.check_button.animate_result(False)
        else:
            self.popup = Popup("No Deadlock Detected", True)
            self.check_button.animate_result(True)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle button clicks
                if self.check_button.rect.collidepoint(mouse_pos):
                    self.check_button.is_clicked(mouse_pos)
                    continue
                    
                if self.process_mode_button.rect.collidepoint(mouse_pos):
                    self.process_mode_button.is_clicked(mouse_pos)
                    continue
                    
                if self.resource_mode_button.rect.collidepoint(mouse_pos):
                    self.resource_mode_button.is_clicked(mouse_pos)
                    continue
                    
                if self.edge_mode_button.rect.collidepoint(mouse_pos):
                    self.edge_mode_button.is_clicked(mouse_pos)
                    continue
                    
                if self.request_edge_button.rect.collidepoint(mouse_pos):
                    self.request_edge_button.is_clicked(mouse_pos)
                    continue
                    
                if self.allocation_edge_button.rect.collidepoint(mouse_pos):
                    self.allocation_edge_button.is_clicked(mouse_pos)
                    continue
                    
                # Don't handle clicks in panel area
                if self.panel.contains_point(mouse_pos):
                    continue
                    
                if event.button == 1:  # Left click
                    if self.current_mode == "edge":
                        # Find clicked node
                        clicked_node = None
                        for process in self.detector.processes.values():
                            if process.contains_point(mouse_pos):
                                clicked_node = process
                                break
                        for resource in self.detector.resources.values():
                            if resource.contains_point(mouse_pos):
                                clicked_node = resource
                                break
                                
                        if clicked_node:
                            if self.edge_start is None:
                                # Start new edge
                                self.edge_start = clicked_node
                                self.popup = Popup("Select second node", True)
                            else:
                                # Complete edge
                                self.create_edge(self.edge_start, clicked_node)
                                self.edge_start = None
                    else:
                        # Add process or resource based on current mode
                        if self.current_mode == "process":
                            process = self.add_process((mouse_pos[0] - 25, mouse_pos[1] - 25))
                            print(f"Created process {process.name} at {process.position}")
                        else:
                            resource = self.add_resource((mouse_pos[0] - 25, mouse_pos[1] - 25))
                            print(f"Created resource {resource.name} at {resource.position}")
                        
                elif event.button == 3:  # Right click
                    # Remove node if clicked
                    for process in list(self.detector.processes.values()):
                        if process.contains_point(mouse_pos):
                            self.detector.remove_process(process)
                            print(f"Removed process {process.name}")
                            break
                    for resource in list(self.detector.resources.values()):
                        if resource.contains_point(mouse_pos):
                            self.detector.remove_resource(resource)
                            print(f"Removed resource {resource.name}")
                            break
                            
            elif event.type == pygame.MOUSEMOTION:
                # Update button hover states
                self.check_button.update(pygame.mouse.get_pos())
                self.process_mode_button.update(pygame.mouse.get_pos())
                self.resource_mode_button.update(pygame.mouse.get_pos())
                self.edge_mode_button.update(pygame.mouse.get_pos())
                self.request_edge_button.update(pygame.mouse.get_pos())
                self.allocation_edge_button.update(pygame.mouse.get_pos())
                
    def update(self, dt):
        # Update animations
        self.animation_time += dt
        if self.animation_time >= 2 * math.pi:
            self.animation_time = 0
            
        # Update background
        self.background.update(dt)
        
        # Update popup
        if self.popup:
            if self.popup.update(dt):
                self.popup = None
                
    def draw(self):
        # Draw background
        self.background.draw(self.screen)
        
        # Draw edges between nodes
        for process in self.detector.processes.values():
            # Draw allocation edges
            for resource in process.allocated:
                start_pos = resource.position  # Resource to Process
                end_pos = process.position
                pygame.draw.line(self.screen, (255, 255, 255),
                               (start_pos[0] + 25, start_pos[1] + 25),
                               (end_pos[0] + 25, end_pos[1] + 25), 2)
                               
            # Draw request edges (dashed)
            for resource in process.requesting:
                start_pos = process.position  # Process to Resource
                end_pos = resource.position
                dash_length = 5
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:  # Avoid division by zero
                    dx /= dist
                    dy /= dist
                    
                    for i in range(0, int(dist), dash_length * 2):
                        start = (start_pos[0] + dx * i + 25,
                                start_pos[1] + dy * i + 25)
                        end = (start_pos[0] + dx * (i + dash_length) + 25,
                              start_pos[1] + dy * (i + dash_length) + 25)
                        if i + dash_length > dist:
                            end = (end_pos[0] + 25, end_pos[1] + 25)
                        pygame.draw.line(self.screen, (200, 200, 200), start, end, 2)
        
        # Draw temporary edge while creating
        if self.edge_start and self.current_mode == "edge":
            mouse_pos = pygame.mouse.get_pos()
            start_pos = (self.edge_start.position[0] + 25, self.edge_start.position[1] + 25)
            if self.edge_type == "request":
                # Draw dashed line for request
                dash_length = 5
                dx = mouse_pos[0] - start_pos[0]
                dy = mouse_pos[1] - start_pos[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    dx /= dist
                    dy /= dist
                    for i in range(0, int(dist), dash_length * 2):
                        start = (start_pos[0] + dx * i, start_pos[1] + dy * i)
                        end = (start_pos[0] + dx * (i + dash_length), start_pos[1] + dy * (i + dash_length))
                        pygame.draw.line(self.screen, (200, 200, 200), start, end, 2)
            else:
                # Draw solid line for allocation
                pygame.draw.line(self.screen, (255, 255, 255), start_pos, mouse_pos, 2)
        
        # Draw nodes
        for process in self.detector.processes.values():
            # Draw glow effect
            glow_radius = 30
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for r in range(glow_radius, 0, -1):
                alpha = int(50 * (1 - r/glow_radius))
                pygame.draw.circle(glow_surface, (*process.color, alpha),
                                 (glow_radius, glow_radius), r)
            self.screen.blit(glow_surface,
                           (process.position[0] + 25 - glow_radius,
                            process.position[1] + 25 - glow_radius))
            
            # Draw main circle
            pygame.draw.circle(self.screen, process.color,
                             (process.position[0] + 25, process.position[1] + 25), 25)
            # Draw process name
            font = pygame.font.Font(None, 36)
            text = font.render(process.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(process.position[0] + 25,
                                            process.position[1] + 25))
            self.screen.blit(text, text_rect)
            
        for resource in self.detector.resources.values():
            # Draw resource as red square
            pygame.draw.rect(self.screen, (200, 50, 50),
                           (resource.position[0], resource.position[1], 50, 50))
            # Draw resource name
            font = pygame.font.Font(None, 36)
            text = font.render(resource.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(resource.position[0] + 25,
                                            resource.position[1] + 25))
            self.screen.blit(text, text_rect)
        
        # Draw UI on top
        self.panel.draw(self.screen)
        self.check_button.draw(self.screen)
        self.process_mode_button.draw(self.screen)
        self.resource_mode_button.draw(self.screen)
        self.edge_mode_button.draw(self.screen)
        self.request_edge_button.draw(self.screen)
        self.allocation_edge_button.draw(self.screen)
        
        if self.popup:
            self.popup.draw(self.screen)
            
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

    def set_edge_type(self, edge_type: str):
        """Set the type of edge to create"""
        self.edge_type = edge_type
        self.request_edge_button.is_active = (edge_type == "request")
        self.allocation_edge_button.is_active = (edge_type == "allocation")

    def create_edge(self, start_node, end_node):
        """Create an edge between two nodes"""
        if self.edge_type == "request":
            if isinstance(start_node, Process) and isinstance(end_node, Resource):
                start_node.request_resource(end_node)
                self.popup = Popup(f"{start_node.name} requested {end_node.name}", True)
            else:
                self.popup = Popup("Request edges must go from Process to Resource", False)
        else:  # allocation
            if isinstance(start_node, Resource) and isinstance(end_node, Process):
                end_node.allocate_resource(start_node)
                self.popup = Popup(f"{start_node.name} allocated to {end_node.name}", True)
            else:
                self.popup = Popup("Allocation edges must go from Resource to Process", False)

if __name__ == "__main__":
    app = DeadlockSimulator()
    app.run()