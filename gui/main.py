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
from gui.game import GameState

# Define colors for different node types
PROCESS_COLORS = [
    (50, 205, 50),    # Lime Green
    (147, 112, 219),  # Purple
    (255, 165, 0)     # Orange
]

class DeadlockDetectionSimulator:
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
        
        # Initialize state
        self.selected_node = None
        self.dragging = False
        self.clock = pygame.time.Clock()
        self.animation_time = 0
        self.next_color_index = 0
        self.current_mode = "process"  # Default mode
        self.edge_start = None
        self.edge_end = None
        self.edge_type = "request"  # Default to request edges
        self.temp_edge_pos = None  # For visual feedback during edge creation
        
        # Initialize deadlock detector
        self.detector = DeadlockDetector()
        
        # Initialize game state
        self.game_state = GameState()
        
        # Initialize background system
        self.background = BackgroundSystem(self.width, self.height)
        
        # Initialize graph
        self.graph = Graph()
        
        # Create instruction panel
        self.setup_ui()
        
        self.popup = None
        self.running = True
        
        # Initialize UI elements with better spacing
        button_width = 180  # Increased width for better text fit
        button_height = 40
        button_margin = 20
        start_x = 20
        start_y = 20
        
        # Create mode buttons in top row
        self.mode_buttons = {
            "process": Button(start_x, start_y, button_width, button_height,
                            "Process Mode (1)", lambda: self.set_mode("process")),
            "resource": Button(start_x + button_width + button_margin, start_y,
                             button_width, button_height, "Resource Mode (2)",
                             lambda: self.set_mode("resource")),
            "edge": Button(start_x + 2 * (button_width + button_margin), start_y,
                         button_width, button_height, "Edge Mode (3)",
                         lambda: self.set_mode("edge"))
        }
        
        # Create edge type buttons in second row
        edge_type_y = start_y + button_height + button_margin
        self.request_edge_button = Button(start_x, edge_type_y,
                                        button_width, button_height, "Request Edge",
                                        lambda: self.set_edge_type("request"))
        self.allocation_edge_button = Button(start_x + button_width + button_margin, edge_type_y,
                                           button_width, button_height, "Allocation Edge",
                                           lambda: self.set_edge_type("allocation"))
        
        # Mode switching cooldown
        self.mode_switch_cooldown = 0
        self.mode_switch_delay = 500  # milliseconds
        
        # Dual mode state
        self.dual_mode = False
        self.dual_mode_toggle_cooldown = 0
        self.dual_mode_toggle_delay = 500  # milliseconds
        
    def setup_ui(self):
        # Create instruction panel with gradient background
        panel_width = 300  # Reduced width
        panel_height = 350  # Reduced height
        
        instructions = [
            "🎮 Keyboard Controls:",
            "• 1 - Process Mode",
            "• 2 - Resource Mode",
            "• 3 - Edge Mode",
            "• D - Toggle Dual Mode",
            "",
            "🖱️ Mouse Controls:",
            "• Left Click - Create/Select",
            "• Drag - Move nodes",
            "• Right Click - Delete",
            "",
            "📝 Mode Instructions:",
            "Process Mode:",
            "• Create process nodes",
            "",
            "Resource Mode:",
            "• Create resource nodes",
            "",
            "Edge Mode:",
            "• Click nodes to connect",
            "",
            "✨ Special Features:",
            "• Dual Mode - Create both",
            "• Check for deadlocks",
            "• Clear to start fresh"
        ]
        
        # Position the panel in the right corner with proper spacing
        panel_x = self.width - panel_width - 10
        panel_y = 10
        
        self.instruction_panel = Panel(panel_x, panel_y, 
                                     panel_width, panel_height, 
                                     "Instructions", instructions)
        
        # Create action buttons
        button_width = 180
        button_height = 40
        button_margin = 10
        
        # Position Check Deadlock button at bottom right corner
        check_button_x = self.width - button_width - 10
        check_button_y = self.height - button_height - 10
        
        # Position Clear Graph button above Check Deadlock button
        clear_button_x = check_button_x
        clear_button_y = check_button_y - button_height - button_margin
        
        self.check_button = Button(check_button_x, check_button_y,
                                 button_width, button_height, "Check Deadlock",
                                 self.check_deadlock)
        self.clear_button = Button(clear_button_x, clear_button_y,
                                 button_width, button_height, "Clear Graph",
                                 self.clear_graph)

    def set_mode(self, new_mode):
        """Switch to a new mode and update UI"""
        self.current_mode = new_mode
        # Update button states
        for mode, button in self.mode_buttons.items():
            button.is_active = (mode == new_mode)

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
        has_deadlock = False
        deadlocked_processes = set()
        
        # Build adjacency lists for the resource allocation graph
        allocation_graph = {}
        request_graph = {}
        
        # Initialize graphs
        for process in self.detector.processes.values():
            allocation_graph[process] = set(process.allocated)
            request_graph[process] = set(process.requesting)
        
        # Check for cycles in the graph
        visited = set()
        path = set()
        
        def dfs(process):
            nonlocal has_deadlock
            if process in path:
                has_deadlock = True
                deadlocked_processes.update(path)
                return
            
            if process in visited:
                return
                
            visited.add(process)
            path.add(process)
            
            # Check resources this process is requesting
            for resource in request_graph[process]:
                # Find processes that have this resource allocated
                for other_process in self.detector.processes.values():
                    if resource in allocation_graph[other_process]:
                        dfs(other_process)
            
            path.remove(process)
        
        # Start DFS from each process
        for process in self.detector.processes.values():
            if process not in visited:
                dfs(process)
        
        if has_deadlock:
            self.popup = Popup("Deadlock Detected!", False)
            self.check_button.animate_result(False)
            # Highlight deadlocked processes
            for process in self.detector.processes.values():
                if process in deadlocked_processes:
                    process.color = (255, 0, 0)  # Red for deadlocked processes
        else:
            self.popup = Popup("No Deadlock Detected", True)
            self.check_button.animate_result(True)
            # Reset process colors
            self.next_color_index = 0
            for process in self.detector.processes.values():
                process.color = self.get_next_process_color()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle button clicks in order of priority
                # First check mode buttons
                for mode, button in self.mode_buttons.items():
                    if button.rect.collidepoint(mouse_pos):
                        self.set_mode(mode)
                        return
                
                # Check edge type buttons
                if self.request_edge_button.rect.collidepoint(mouse_pos):
                    self.set_edge_type("request")
                    return
                    
                if self.allocation_edge_button.rect.collidepoint(mouse_pos):
                    self.set_edge_type("allocation")
                    return
                
                # Check action buttons
                if self.check_button.rect.collidepoint(mouse_pos):
                    self.check_deadlock()
                    return
                    
                if self.clear_button.rect.collidepoint(mouse_pos):
                    self.clear_graph()
                    return
                    
                # Don't handle clicks in panel area
                if self.instruction_panel.contains_point(mouse_pos):
                    return
                    
                # Handle node creation/selection
                if event.button == 1:  # Left click
                    if self.current_mode == "edge":
                        self.start_edge(mouse_pos)
                    else:
                        self.handle_node_click(mouse_pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(mouse_pos)
                    
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                # Update button hover states
                for button in self.mode_buttons.values():
                    button.update(mouse_pos)
                self.request_edge_button.update(mouse_pos)
                self.allocation_edge_button.update(mouse_pos)
                self.check_button.update(mouse_pos)
                self.clear_button.update(mouse_pos)
                
                # Handle dragging and edge preview
                self.handle_mouse_motion(mouse_pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_release(pygame.mouse.get_pos())
                
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard_input(event)

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
        
        # Draw temporary edge during creation
        if self.edge_start and self.temp_edge_pos and self.current_mode == "edge":
            color = (0, 255, 0) if self.edge_type == "request" else (255, 165, 0)
            start_pos = (self.edge_start.position[0] + 25, self.edge_start.position[1] + 25)
            pygame.draw.line(self.screen, color, start_pos, self.temp_edge_pos, 2)
            
            # Draw arrow at the end
            angle = math.atan2(self.temp_edge_pos[1] - start_pos[1],
                             self.temp_edge_pos[0] - start_pos[0])
            arrow_length = 20
            arrow_angle = math.pi / 6
            end_x = self.temp_edge_pos[0] - arrow_length * math.cos(angle)
            end_y = self.temp_edge_pos[1] - arrow_length * math.sin(angle)
            pygame.draw.line(self.screen, color, self.temp_edge_pos, 
                           (end_x + arrow_length * math.cos(angle + arrow_angle),
                            end_y + arrow_length * math.sin(angle + arrow_angle)), 2)
            pygame.draw.line(self.screen, color, self.temp_edge_pos,
                           (end_x + arrow_length * math.cos(angle - arrow_angle),
                            end_y + arrow_length * math.sin(angle - arrow_angle)), 2)
        
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
        
        # Draw UI elements in correct order
        # First draw mode buttons
        for button in self.mode_buttons.values():
            button.draw(self.screen)
            
        # Draw edge type buttons
        self.request_edge_button.draw(self.screen)
        self.allocation_edge_button.draw(self.screen)
        
        # Draw action buttons
        self.check_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        
        # Draw instruction panel
        self.instruction_panel.draw(self.screen)
        
        # Draw popup last (on top)
        if self.popup:
            self.popup.draw(self.screen)
            
    def run(self):
        self.dragging_node = None
        self.drag_offset = (0, 0)
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.animation_time += dt
            
            mouse_pos = pygame.mouse.get_pos()  # Get current mouse position
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keyboard_input(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos, event.button)
                elif event.type == pygame.MOUSEWHEEL:
                    # Handle scrolling for instruction panel
                    if self.instruction_panel.contains_point(mouse_pos):
                        self.instruction_panel.handle_scroll(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_release(event.pos)
            
            # Update
            self.update(dt)
            
            # Draw
            self.screen.fill(PANEL_BG)
            self.background.draw(self.screen)
            self.draw()
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def set_edge_type(self, edge_type: str):
        """Set the type of edge to create"""
        self.edge_type = edge_type
        self.request_edge_button.is_active = (edge_type == "request")
        self.allocation_edge_button.is_active = (edge_type == "allocation")
        # Clear any existing edge creation state
        self.edge_start = None
        self.edge_end = None
        self.temp_edge_pos = None

    def create_edge(self, start_node, end_node):
        """Create an edge between two nodes"""
        if self.edge_type == "request":
            if isinstance(start_node, Process) and isinstance(end_node, Resource):
                # Process requesting resource
                start_node.request_resource(end_node)
                self.popup = Popup(f"{start_node.name} requested {end_node.name}", True)
            elif isinstance(start_node, Resource) and isinstance(end_node, Process):
                # Process requesting resource (reverse order)
                end_node.request_resource(start_node)
                self.popup = Popup(f"{end_node.name} requested {start_node.name}", True)
            else:
                self.popup = Popup("Invalid request edge: Must connect Process and Resource", False)
        else:  # allocation edge
            if isinstance(start_node, Resource) and isinstance(end_node, Process):
                # Resource allocated to process
                if start_node not in end_node.allocated:
                    end_node.allocated.add(start_node)
                    self.popup = Popup(f"{start_node.name} allocated to {end_node.name}", True)
                else:
                    self.popup = Popup(f"{start_node.name} already allocated to {end_node.name}", False)
            elif isinstance(start_node, Process) and isinstance(end_node, Resource):
                # Resource allocated to process (reverse order)
                if end_node not in start_node.allocated:
                    start_node.allocated.add(end_node)
                    self.popup = Popup(f"{end_node.name} allocated to {start_node.name}", True)
                else:
                    self.popup = Popup(f"{end_node.name} already allocated to {start_node.name}", False)
            else:
                self.popup = Popup("Invalid allocation edge: Must connect Resource and Process", False)

    def handle_keyboard_input(self, event):
        current_time = pygame.time.get_ticks()
        
        # Handle mode switching with number keys
        if event.type == pygame.KEYDOWN and current_time - self.mode_switch_cooldown > self.mode_switch_delay:
            if event.key == pygame.K_1:
                self.set_mode('process')
                self.mode_switch_cooldown = current_time
            elif event.key == pygame.K_2:
                self.set_mode('resource')
                self.mode_switch_cooldown = current_time
            elif event.key == pygame.K_3:
                self.set_mode('edge')
                self.mode_switch_cooldown = current_time
            elif event.key == pygame.K_d:  # Toggle dual mode with 'D' key
                if current_time - self.dual_mode_toggle_cooldown > self.dual_mode_toggle_delay:
                    self.dual_mode = not self.dual_mode
                    self.dual_mode_toggle_cooldown = current_time
                    # Show feedback popup
                    self.show_mode_feedback()

    def show_mode_feedback(self):
        if self.dual_mode:
            self.show_popup("Dual Mode Enabled", "You can now create both processes and resources simultaneously.", True)
        else:
            self.show_popup("Dual Mode Disabled", "Switched back to single mode.", True)

    def show_popup(self, title: str, message: str, success: bool):
        self.game_state.active_popup = Popup(title, message, success)

    def handle_mouse_click(self, pos: Tuple[int, int], button: int):
        """Handle mouse click"""
        # Check mode button clicks
        for btn in self.mode_buttons.values():
            if btn.is_clicked(pos):
                self.set_mode(btn.text.lower().split()[0])
                return
                
        # Check action button clicks
        if self.check_button.is_clicked(pos):
            self.check_deadlock()
            return
        if self.clear_button.is_clicked(pos):
            self.clear_graph()
            return
            
        # Check edge type button clicks
        if self.request_edge_button.is_clicked(pos):
            self.set_edge_type("request")
            return
        if self.allocation_edge_button.is_clicked(pos):
            self.set_edge_type("allocation")
            return
            
        # Handle node dragging
        if button == 1:  # Left click
            if self.current_mode == "edge":
                self.start_edge(pos)
            else:
                # Find clicked node
                clicked_node = None
                for process in self.detector.processes.values():
                    if process.contains_point(pos):
                        clicked_node = process
                        break
                for resource in self.detector.resources.values():
                    if resource.contains_point(pos):
                        clicked_node = resource
                        break
                        
                if clicked_node:
                    self.dragging_node = clicked_node
                    self.drag_offset = (pos[0] - clicked_node.position[0], 
                                      pos[1] - clicked_node.position[1])
                else:
                    # Create new node if not clicking on existing node
                    if self.current_mode == "process":
                        self.create_process(pos)
                    elif self.current_mode == "resource":
                        self.create_resource(pos)
                
        elif button == 3:  # Right click
            self.handle_right_click(pos)

    def handle_mouse_motion(self, pos):
        """Handle mouse motion"""
        # Update dragging if active
        if self.dragging_node:
            self.dragging_node.position = (pos[0] - self.drag_offset[0], 
                                         pos[1] - self.drag_offset[1])
        
        # Update temporary edge position for visual feedback
        if self.edge_start and self.current_mode == "edge":
            self.temp_edge_pos = pos

    def handle_mouse_release(self, pos: Tuple[int, int]):
        # Clear dragging state
        self.dragging_node = None
        self.drag_offset = (0, 0)

    def clear_graph(self):
        self.detector.clear_graph()
        self.popup = Popup("Graph cleared", True)

    def create_process(self, pos: Tuple[int, int]):
        """Create a new process at the given position"""
        process = self.add_process((pos[0] - 25, pos[1] - 25))
        print(f"Created process {process.name} at {process.position}")
        return process

    def create_resource(self, pos: Tuple[int, int]):
        """Create a new resource at the given position"""
        resource = self.add_resource((pos[0] - 25, pos[1] - 25))
        print(f"Created resource {resource.name} at {resource.position}")
        return resource

    def handle_right_click(self, pos: Tuple[int, int]):
        """Handle right-click events (node deletion)"""
        # Check if we clicked on a process
        for process in list(self.detector.processes.values()):
            if process.contains_point(pos):
                self.detector.remove_process(process)
                return
            
        # Check if we clicked on a resource
        for resource in list(self.detector.resources.values()):
            if resource.contains_point(pos):
                self.detector.remove_resource(resource)
                return

    def start_edge(self, pos):
        """Start creating an edge from a clicked node"""
        # Find clicked node
        clicked_node = None
        for process in self.detector.processes.values():
            if process.contains_point(pos):
                clicked_node = process
                break
        for resource in self.detector.resources.values():
            if resource.contains_point(pos):
                clicked_node = resource
                break
                
        if clicked_node:
            if self.edge_start is None:
                # Start new edge
                self.edge_start = clicked_node
                self.temp_edge_pos = pos
                self.popup = Popup("Select second node", True)
            else:
                # Complete edge
                self.edge_end = clicked_node
                if self.edge_start != self.edge_end:  # Prevent self-loops
                    self.create_edge(self.edge_start, self.edge_end)
                self.edge_start = None
                self.edge_end = None
                self.temp_edge_pos = None

    def draw_grid(self):
        """Draw the background grid"""
        grid_size = 50
        grid_color = (40, 40, 40, 30)  # Subtle grid color
        
        # Draw vertical lines
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height))
            
        # Draw horizontal lines
        for y in range(0, self.height, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y))

if __name__ == "__main__":
    app = DeadlockDetectionSimulator()
    app.run()