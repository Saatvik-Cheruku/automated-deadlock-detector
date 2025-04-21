import pygame
import sys
import math
from typing import List, Tuple, Optional
from gui.ui_utils import Button, Panel, Popup, PRIMARY_COLOR, SECONDARY_COLOR, PANEL_BG, TEXT_COLOR, GRID_COLOR
from deadlock_detector import DeadlockDetector
from process import Process, Resource

class GameState:
    def __init__(self):
        self.current_mode = 'process'  # Default mode
        self.edge_start = None  # For edge creation
        self.active_popup: Optional[Popup] = None
        self.animation_time = 0

    def update(self, dt: float):
        """Update game state"""
        self.animation_time += dt
        if self.animation_time >= 2 * 3.14159:  # Reset after one full cycle
            self.animation_time = 0

        # Update active popup if exists
        if self.active_popup:
            if self.active_popup.update(dt):
                self.active_popup = None

class Game:
    def __init__(self):
        pygame.init()
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Deadlock Detection Simulator")
        
        # Initialize game state
        self.processes: List[Process] = []
        self.resources: List[Resource] = []
        self.detector = DeadlockDetector()
        self.selected_process: Optional[Process] = None
        self.selected_resource: Optional[Resource] = None
        self.popups: List[Popup] = []
        self.dragging = False
        self.drag_offset = (0, 0)
        self.drag_target = None
        
        # Grid settings
        self.grid_size = 40
        self.grid_offset_x = 0
        self.grid_offset_y = 0
        
        # Initialize UI components
        self.setup_ui()
        
        # Initialize game state
        self.game_state = GameState()
        
    def setup_ui(self):
        button_width = 180
        button_height = 40
        button_spacing = 20
        panel_width = 300
        
        # Create buttons
        self.buttons = [
            Button(20, 20, button_width, button_height, 
                  "Add Process", lambda: self.add_process()),
            Button(20, 20 + button_height + button_spacing, button_width, button_height,
                  "Add Resource", lambda: self.add_resource()),
            Button(20, 20 + (button_height + button_spacing) * 2, button_width, button_height,
                  "Check Deadlock", lambda: self.check_deadlock()),
            Button(20, 20 + (button_height + button_spacing) * 3, button_width, button_height,
                  "Clear All", lambda: self.clear_all()),
        ]
        
        # Create instruction panel
        instructions = [
            "Left click to select/drag",
            "Right click to delete",
            "",
            "To create a request:",
            "1. Select a process",
            "2. Click a resource",
            "",
            "To allocate a resource:",
            "1. Select a resource",
            "2. Click a process"
        ]
        
        self.panel = Panel(
            self.width - panel_width - 20, 20,
            panel_width, self.height - 40,
            "Instructions", instructions
        )
        
    def add_process(self):
        process = Process(f"P{len(self.processes)}")
        # Position process on grid
        grid_x = (len(self.processes) % 3) * 200 + 300
        grid_y = (len(self.processes) // 3) * 150 + 100
        process.x = grid_x
        process.y = grid_y
        self.processes.append(process)
        self.show_popup(f"Added {process.name}", True)
        
    def add_resource(self):
        resource = Resource(f"R{len(self.resources)}")
        # Position resource on grid
        grid_x = (len(self.resources) % 3) * 200 + 300
        grid_y = (len(self.resources) // 3) * 150 + 300
        resource.x = grid_x
        resource.y = grid_y
        self.resources.append(resource)
        self.show_popup(f"Added {resource.name}", True)
        
    def clear_all(self):
        self.processes.clear()
        self.resources.clear()
        self.selected_process = None
        self.selected_resource = None
        self.show_popup("Cleared all elements", True)
        
    def check_deadlock(self):
        if not self.processes or not self.resources:
            self.show_popup("Add processes and resources first", False)
            return
            
        deadlock = self.detector.detect_deadlock(self.processes, self.resources)
        if deadlock:
            message = "Deadlock detected!"
            self.show_popup(message, False)
        else:
            message = "No deadlock found"
            self.show_popup(message, True)
            
    def show_popup(self, message: str, success: bool):
        self.popups.append(Popup(message, success))
        
    def handle_click(self, pos: Tuple[int, int], right_click: bool = False):
        if right_click:
            # Handle deletion
            for process in self.processes[:]:
                if process.contains_point(pos):
                    self.processes.remove(process)
                    self.show_popup(f"Deleted {process.name}", True)
                    return
                    
            for resource in self.resources[:]:
                if resource.contains_point(pos):
                    self.resources.remove(resource)
                    self.show_popup(f"Deleted {resource.name}", True)
                    return
        else:
            # Handle selection and connection
            for process in self.processes:
                if process.contains_point(pos):
                    if self.selected_resource:
                        # Allocate resource to process
                        self.detector.allocate(self.selected_resource, process)
                        self.show_popup(f"Allocated {self.selected_resource.name} to {process.name}", True)
                        self.selected_resource = None
                    else:
                        # Select process
                        self.selected_process = process if process != self.selected_process else None
                        self.selected_resource = None
                    return
                    
            for resource in self.resources:
                if resource.contains_point(pos):
                    if self.selected_process:
                        # Create request from process to resource
                        self.detector.request(self.selected_process, resource)
                        self.show_popup(f"{self.selected_process.name} requested {resource.name}", True)
                        self.selected_process = None
                    else:
                        # Select resource
                        self.selected_resource = resource if resource != self.selected_resource else None
                        self.selected_process = None
                    return
                    
            # If clicked empty space, clear selection
            self.selected_process = None
            self.selected_resource = None
            
    def handle_drag_start(self, pos: Tuple[int, int]):
        for process in self.processes:
            if process.contains_point(pos):
                self.dragging = True
                self.drag_target = process
                self.drag_offset = (pos[0] - process.x, pos[1] - process.y)
                return
                
        for resource in self.resources:
            if resource.contains_point(pos):
                self.dragging = True
                self.drag_target = resource
                self.drag_offset = (pos[0] - resource.x, pos[1] - resource.y)
                return
                
    def handle_drag(self, pos: Tuple[int, int]):
        if self.dragging and self.drag_target:
            self.drag_target.x = pos[0] - self.drag_offset[0]
            self.drag_target.y = pos[1] - self.drag_offset[1]
            
    def handle_drag_end(self):
        self.dragging = False
        self.drag_target = None
        
    def draw_grid(self):
        # Draw background grid
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(self.screen, GRID_COLOR,
                           (x + self.grid_offset_x, 0),
                           (x + self.grid_offset_x, self.height), 1)
                           
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(self.screen, GRID_COLOR,
                           (0, y + self.grid_offset_y),
                           (self.width, y + self.grid_offset_y), 1)
                           
    def draw_connections(self):
        # Draw allocation arrows (solid lines)
        for resource in self.resources:
            if resource.allocated_to:
                start_pos = (resource.x + 25, resource.y + 25)
                end_pos = (resource.allocated_to.x + 25, resource.allocated_to.y + 25)
                self.draw_arrow(start_pos, end_pos, PRIMARY_COLOR, True)
                
        # Draw request arrows (dashed lines)
        for process in self.processes:
            for resource in process.requesting:
                start_pos = (process.x + 25, process.y + 25)
                end_pos = (resource.x + 25, resource.y + 25)
                self.draw_arrow(start_pos, end_pos, SECONDARY_COLOR, False)
                
    def draw_arrow(self, start: Tuple[int, int], end: Tuple[int, int], 
                  color: Tuple[int, int, int], solid: bool):
        # Calculate arrow properties
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        length = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        # Adjust end point to stop at circle edge
        end = (start[0] + (length - 35) * math.cos(angle),
               start[1] + (length - 35) * math.sin(angle))
               
        # Draw line
        if solid:
            pygame.draw.line(self.screen, color, start, end, 2)
        else:
            # Draw dashed line
            dash_length = 10
            dash_gap = 5
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            dash_count = int(length / (dash_length + dash_gap))
            
            for i in range(dash_count):
                dash_start = (start[0] + dx * i / dash_count,
                            start[1] + dy * i / dash_count)
                dash_end = (start[0] + dx * (i + 0.5) / dash_count,
                          start[1] + dy * (i + 0.5) / dash_count)
                pygame.draw.line(self.screen, color, dash_start, dash_end, 2)
                
        # Draw arrow head
        arrow_size = 10
        arrow_angle = 0.5  # 30 degrees in radians
        
        arrow_point1 = (end[0] - arrow_size * math.cos(angle - arrow_angle),
                       end[1] - arrow_size * math.sin(angle - arrow_angle))
        arrow_point2 = (end[0] - arrow_size * math.cos(angle + arrow_angle),
                       end[1] - arrow_size * math.sin(angle + arrow_angle))
                       
        pygame.draw.polygon(self.screen, color, [end, arrow_point1, arrow_point2])
        
    def draw_nodes(self):
        # Draw processes
        for process in self.processes:
            color = PRIMARY_COLOR if process == self.selected_process else PANEL_BG
            pygame.draw.circle(self.screen, color, (process.x + 25, process.y + 25), 25)
            pygame.draw.circle(self.screen, PRIMARY_COLOR, (process.x + 25, process.y + 25), 25, 2)
            
            # Draw process name
            font = pygame.font.Font(None, 36)
            text = font.render(process.name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(process.x + 25, process.y + 25))
            self.screen.blit(text, text_rect)
            
        # Draw resources
        for resource in self.resources:
            color = PRIMARY_COLOR if resource == self.selected_resource else PANEL_BG
            pygame.draw.rect(self.screen, color,
                           (resource.x, resource.y, 50, 50))
            pygame.draw.rect(self.screen, PRIMARY_COLOR,
                           (resource.x, resource.y, 50, 50), 2)
            
            # Draw resource name
            font = pygame.font.Font(None, 36)
            text = font.render(resource.name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(resource.x + 25, resource.y + 25))
            self.screen.blit(text, text_rect)
            
    def update(self, dt: float):
        # Update popups
        self.popups = [popup for popup in self.popups if not popup.update(dt)]
        
        # Update game state
        self.game_state.update(dt)
        
    def draw(self):
        # Fill background
        self.screen.fill(PANEL_BG)
        
        # Draw grid
        self.draw_grid()
        
        # Draw connections
        self.draw_connections()
        
        # Draw nodes
        self.draw_nodes()
        
        # Draw UI elements
        for button in self.buttons:
            button.draw(self.screen)
            
        self.panel.draw(self.screen)
        
        # Draw popups
        for popup in self.popups:
            popup.draw(self.screen)
            
        # Update display
        pygame.display.flip()
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0  # Convert to seconds
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Check UI elements first
                    ui_handled = False
                    for button in self.buttons:
                        if button.is_clicked(pos):
                            ui_handled = True
                            break
                            
                    if not ui_handled and not self.panel.contains_point(pos):
                        if event.button == 1:  # Left click
                            self.handle_drag_start(pos)
                        elif event.button == 3:  # Right click
                            self.handle_click(pos, right_click=True)
                            
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click
                        if not self.dragging:
                            self.handle_click(pygame.mouse.get_pos())
                        self.handle_drag_end()
                        
                elif event.type == pygame.MOUSEMOTION:
                    # Update button hover states
                    for button in self.buttons:
                        button.update(event.pos)
                        
                    if self.dragging:
                        self.handle_drag(event.pos)
                        
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 