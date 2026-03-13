# MapGraph

An interactive graph visualization program that allows you to create and manage nodes and connections between nodes on a map with Dijkstra pathfinding algorithm.

![MapGraph-screenshot](/img/readme/ss1.png)

## Main Features

- **Pin Node**: Create named nodes to mark important locations (start/end points)
- **Default Node**: Create regular nodes as intermediate vertices
- **Connect Nodes**: Connect two nodes with edges (lines) and distance weights
- **Remove Node**: Delete unwanted nodes
- **Dijkstra**: Find the shortest path between two nodes
- **Export/Import**: Save and load graph configurations in JSON format
- **Background Map**: Support for various background map images

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- Pillow (PIL) for image processing

## Installation

```bash
pip install Pillow
```

## How to Use

1. **Run the Program**
   ```bash
   python map_demo.py
   ```

2. **Creating Nodes**
   - Click the **Pin Node** button to create a named node (click on canvas, input name when prompted)
   - Click the **Default Node** button to create a regular node (click directly on canvas)

3. **Connecting Nodes**
   - Click the **Connect Nodes** button
   - Click the first node, then click the second node
   - Input the weight/distance between nodes when prompted

4. **Finding the Shortest Path**
   - Click the **Djikstra** button
   - Select the start node and destination node
   - The shortest path will be displayed on the canvas

5. **Removing Nodes**
   - Click the **Remove Node** button
   - Click the node you want to delete

6. **Save & Load**
   - **Export**: Save the graph to a new JSON file
   - **Import**: Load a graph from an existing JSON file

## File Structure

- `map_demo.py` - Main program
- `config.json` - Default node data for general map
- `config_map_ITS.json` - Node data specific to ITS map
- `config_map_JakartaBandung.json` - Node data specific to Jakarta-Bandung map
- `img/` - Folder containing background map images

## Canvas Controls

- **Default mode**: Click to view node information
- **LMB (Left Mouse Button)**: Use according to the selected mode
