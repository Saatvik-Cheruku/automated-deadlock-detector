# Automated Deadlock Detection Simulator

A Python-based simulation tool that demonstrates deadlock detection in operating systems using Resource Allocation Graphs (RAG).

## Features

- Interactive Resource Allocation Graph (RAG) visualization
- Real-time deadlock detection using DFS algorithm
- Visual feedback for deadlock status
- Intuitive node and edge creation through mouse interaction
- Reset functionality to clear the graph

## Installation

### For Windows Users (Downloading from Website)

1. **Install Python**:
   - Download Python from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"
   - Choose "Install Now" with default settings
   - Verify installation by opening Command Prompt and typing:
     ```bash
     python --version
     ```

2. **Install Dependencies**:
   - Open Command Prompt (cmd)
   - Navigate to the project directory:
     ```bash
     cd path\to\automated-deadlock-detector
     ```
   - Install requirements:
     ```bash
     python -m pip install -r requirements.txt
     ```

### For Developers (Using Git)

1. Clone the repository:
```bash
git clone <repository-url>
cd automated-deadlock-detector
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

## Usage

Run the simulation:
```bash
cd gui
python main.py
```

### How to Use the Simulator

1. **Creating Nodes**:
   - Click on the canvas to create process nodes (P0, P1, etc.)
   - Click on the canvas to create resource nodes (R0, R1, etc.)

2. **Creating Edges**:
   - Click on a process node, then click on a resource node to create a request edge
   - Click on a resource node, then click on a process node to create an allocation edge

3. **Checking for Deadlocks**:
   - Click the "Check Deadlock" button to run the deadlock detection algorithm
   - The status will be displayed at the top of the window

4. **Resetting the Graph**:
   - Click the "Reset" button to clear the graph and start over

## Project Structure

```
automated-deadlock-detector/
├── gui/
│   ├── main.py
│   ├── graph.py
│   ├── node.py
│   ├── edge.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## License

MIT License