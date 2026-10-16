# Routing Algorithm Visualizer

An interactive **Data Communication and Networking (DCN) mini-project** that visualizes network routing and shortest-path algorithms using Python and Streamlit.

## 🌐 Live Demo

**[Launch Routing Algorithm Visualizer](https://routing-algorithm-visualizer-syzcdgscf3tzx3xvg5iaek.streamlit.app/)**

**GitHub Repository:** [routing-algorithm-visualizer](https://github.com/shindeyog03-png/routing-algorithm-visualizer)

## 📌 Project Overview

Routing is an essential function of computer networks. Routers determine suitable paths for forwarding packets from a source node to a destination node based on network topology and link costs.

The Routing Algorithm Visualizer provides an interactive way to understand how routing algorithms calculate shortest paths. Users can explore a network topology, observe algorithm execution step by step, compare routing algorithms, and simulate link failures to understand how network routes change.

## 🎯 Objectives

- Understand shortest-path routing in computer networks.
- Visualize network topology and link costs.
- Demonstrate Dijkstra's and Bellman–Ford algorithms.
- Observe algorithm execution through step-by-step navigation and animation.
- Compare routing results for a selected source and destination.
- Simulate link failures and study route recalculation.

## ✨ Features

- **Interactive Network Topology:** Visualize routers as nodes and communication links as weighted edges.
- **Dijkstra's Algorithm:** Calculate shortest paths using non-negative link costs.
- **Bellman–Ford Algorithm:** Calculate shortest paths through iterative edge relaxation.
- **Step-by-Step Visualization:** Navigate through algorithm execution using previous and next controls.
- **Play Animation:** Observe routing progress dynamically.
- **Algorithm Comparison:** Compare Dijkstra and Bellman–Ford using the same source and destination.
- **Link Failure Simulation:** Disable a network link and observe how the available route changes.
- **Distance Table:** Track the calculated distances to network nodes during algorithm execution.

## 🧠 Algorithms Used

### 1. Dijkstra's Algorithm

Dijkstra's algorithm finds shortest paths from a selected source node to other nodes in a graph with non-negative edge weights.

**Working:**
1. Initialize the source distance to zero and other distances to infinity.
2. Select the unvisited node with the smallest known distance.
3. Update the distances of its neighboring nodes if a shorter route is found.
4. Repeat until the reachable nodes have been processed.

### 2. Bellman–Ford Algorithm

Bellman–Ford calculates shortest paths by repeatedly relaxing the edges of a weighted graph. It can handle negative edge weights and detect reachable negative-weight cycles.

**Working:**
1. Initialize the source distance to zero and other distances to infinity.
2. Relax all edges repeatedly for up to \(V-1\) iterations, where \(V\) is the number of vertices.
3. Check for a further distance improvement to detect a negative-weight cycle.

For a network with non-negative link costs, both algorithms should produce the same shortest-path distances when a path exists.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| NetworkX | Graph and network operations |
| Plotly | Interactive network visualization |
| Pandas | Tabular data and distance tables |
| Git and GitHub | Version control and source-code hosting |
| Streamlit Community Cloud | Application deployment |

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.9 or a compatible version supported by the installed dependencies
- Git
- Visual Studio Code or another Python editor

### Step 1: Clone the repository

```bash
git clone https://github.com/shindeyog03-png/routing-algorithm-visualizer.git
```

### Step 2: Navigate to the project folder

```bash
cd routing-algorithm-visualizer
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Run the application

```bash
python -m streamlit run Routing_Algorithm_Visualizer_fixed.py
```

### Step 5: Open the application

Streamlit will display a local URL in the terminal, usually:

```text
http://localhost:8501
```

Open the URL in your browser.

## 🚀 How to Use

1. Open the [live application](https://routing-algorithm-visualizer-syzcdgscf3tzx3xvg5iaek.streamlit.app/).
2. Explore the displayed network topology and link costs.
3. Select the required source and destination nodes.
4. Run Dijkstra's or Bellman–Ford algorithm.
5. Use the step navigation or animation to observe the routing process.
6. Compare the algorithms' results.
7. Simulate a link failure and observe the recalculated route.

## 🧪 Testing

The application can be tested using the following scenarios:

- Verify shortest-path distances on a small network with known link costs.
- Compare the results of Dijkstra's and Bellman–Ford algorithms.
- Check that step navigation updates the displayed algorithm state.
- Verify that link failure causes the route to be recalculated when an alternative path exists.
- Test a disconnected network to verify how unreachable destinations are handled.

## 📚 Applications

- Learning shortest-path routing concepts.
- Demonstrating graph algorithms in computer networking.
- Understanding the impact of link failures on network connectivity.
- Academic demonstrations and DCN laboratory assignments.

## 🔮 Future Enhancements

- Add additional routing algorithms, such as Floyd–Warshall.
- Support custom network topology creation.
- Allow users to add routers and configure link costs.
- Display packet-routing paths and hop-by-hop information.
- Add performance comparisons for larger network topologies.
- Support importing network topologies from files.

## 👨‍💻 Author

**Yogesh Shinde**

GitHub: [@shindeyog03-png](https://github.com/shindeyog03-png)

## 📄 License

This project is intended for educational and academic purposes. Add an open-source license if you wish to specify permissions for reuse and distribution.

---

⭐ If you find this project useful for learning computer networking and routing algorithms, consider starring the repository.
