import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Set page config
st.set_page_config(
    page_title="Deadlock Detection Tool",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🔒 Deadlock Detection Tool")
st.markdown("""
    This tool helps you visualize and detect deadlocks in resource allocation graphs.
    Add nodes and edges to create your graph, and the tool will automatically detect any deadlocks.
    """)

# Initialize session state for graph
if 'graph' not in st.session_state:
    st.session_state.graph = nx.DiGraph()

# Sidebar for controls
with st.sidebar:
    st.header("Graph Controls")
    
    # Node management
    st.subheader("Add Node")
    node_type = st.radio("Node Type", ["Process", "Resource"])
    node_id = st.text_input("Node ID")
    if st.button("Add Node"):
        if node_id:
            st.session_state.graph.add_node(node_id, type=node_type)
            st.success(f"Added {node_type} node: {node_id}")
        else:
            st.error("Please enter a node ID")

    # Edge management
    st.subheader("Add Edge")
    col1, col2 = st.columns(2)
    with col1:
        from_node = st.selectbox("From", list(st.session_state.graph.nodes()))
    with col2:
        to_node = st.selectbox("To", list(st.session_state.graph.nodes()))
    if st.button("Add Edge"):
        if from_node and to_node:
            st.session_state.graph.add_edge(from_node, to_node)
            st.success(f"Added edge: {from_node} → {to_node}")

    # Clear graph
    if st.button("Clear Graph"):
        st.session_state.graph = nx.DiGraph()
        st.success("Graph cleared")

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Graph Visualization")
    if st.session_state.graph.nodes():
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Draw graph
        pos = nx.spring_layout(st.session_state.graph)
        node_colors = ['lightblue' if st.session_state.graph.nodes[n]['type'] == 'Process' else 'lightgreen' 
                      for n in st.session_state.graph.nodes()]
        
        nx.draw(st.session_state.graph, pos, with_labels=True, node_color=node_colors,
                node_size=2000, font_size=12, font_weight='bold', ax=ax)
        
        # Convert plot to image
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        
        # Display image
        st.markdown(f'<img src="data:image/png;base64,{img_str}" style="width:100%">', 
                   unsafe_allow_html=True)
    else:
        st.info("Add nodes and edges to visualize the graph")

with col2:
    st.subheader("Deadlock Analysis")
    if st.session_state.graph.nodes():
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(st.session_state.graph))
            if cycles:
                st.error("⚠️ Deadlock Detected!")
                st.write("Cycles found:")
                for i, cycle in enumerate(cycles, 1):
                    st.write(f"Cycle {i}: {' → '.join(cycle)} → {cycle[0]}")
            else:
                st.success("✅ No deadlocks detected")
        except nx.NetworkXNoCycle:
            st.success("✅ No deadlocks detected")
    else:
        st.info("Add nodes and edges to perform deadlock analysis")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Created with ❤️ by Saatvik Cheruku</p>
        <p>View source code on <a href='https://github.com/Saatvik-Cheruku/automated-deadlock-detector'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True) 