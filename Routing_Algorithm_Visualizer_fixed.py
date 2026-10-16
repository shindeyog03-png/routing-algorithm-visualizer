import time
import streamlit as st
import networkx as nx
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# Routing Algorithm Visualizer — DCN mini-project
# ============================================================

st.set_page_config(
    page_title="Routing Algorithm Visualizer",
    page_icon="🌐",
    layout="wide",
)

st.title("🌐 Routing Algorithm Visualizer")
st.caption("Data Communication and Networking | Shortest-path routing simulation")


# ---------------- SAMPLE NETWORK ----------------
def create_sample_graph():
    graph = nx.Graph()
    edges = [
        ("R1", "R2", 4),
        ("R1", "R3", 2),
        ("R2", "R3", 1),
        ("R2", "R4", 5),
        ("R3", "R4", 8),
        ("R3", "R5", 10),
        ("R4", "R5", 2),
        ("R4", "R6", 6),
        ("R5", "R6", 3),
    ]
    for u, v, cost in edges:
        graph.add_edge(u, v, weight=cost)
    return graph


if "graph" not in st.session_state:
    st.session_state.graph = create_sample_graph()
if "step_index" not in st.session_state:
    st.session_state.step_index = 0
if "step_slider" not in st.session_state:
    st.session_state.step_slider = 0

G = st.session_state.graph


# ---------------- ROUTING TRACE HELPERS ----------------
def format_distance(value):
    return "∞" if value == float("inf") else f"{value:g}"


def dijkstra_trace(graph, source):
    """Return a sequence of snapshots illustrating Dijkstra's algorithm."""
    distances = {node: float("inf") for node in graph.nodes}
    previous = {node: None for node in graph.nodes}
    distances[source] = 0
    visited = set()
    history = []

    def snapshot(message, current=None):
        history.append({
            "message": message,
            "current": current,
            "distances": distances.copy(),
            "explored": visited.copy(),
            "previous": previous.copy(),
        })

    snapshot(f"Start at source router {source}. Its distance is 0; all others are infinity.")
    while True:
        candidates = [n for n in graph.nodes if n not in visited and distances[n] < float("inf")]
        if not candidates:
            break
        current = min(candidates, key=lambda n: distances[n])
        visited.add(current)
        snapshot(f"Select {current}, the unvisited router with the lowest known distance ({format_distance(distances[current])}).", current)

        for neighbor, edge_data in graph[current].items():
            if neighbor in visited:
                continue
            new_distance = distances[current] + edge_data.get("weight", 1)
            if new_distance < distances[neighbor]:
                old = distances[neighbor]
                distances[neighbor] = new_distance
                previous[neighbor] = current
                snapshot(
                    f"Update {neighbor}: {format_distance(old)} → {format_distance(new_distance)} via {current}.",
                    current,
                )
            else:
                snapshot(
                    f"Check link {current}–{neighbor}: no shorter route found (candidate cost {format_distance(new_distance)}).",
                    current,
                )
    snapshot("Dijkstra finished. The distance estimates are final.")
    return history


def bellman_ford_trace(graph, source):
    """Return snapshots for Bellman–Ford edge relaxation."""
    nodes = list(graph.nodes)
    edges = []
    for u, v, data in graph.edges(data=True):
        weight = data.get("weight", 1)
        edges.append((u, v, weight))
        edges.append((v, u, weight))  # graph is undirected

    distances = {node: float("inf") for node in nodes}
    previous = {node: None for node in nodes}
    distances[source] = 0
    history = []

    def snapshot(message, current=None, explored=None):
        history.append({
            "message": message,
            "current": current,
            "distances": distances.copy(),
            "explored": set(explored or []),
            "previous": previous.copy(),
        })

    snapshot(f"Start at source router {source}. Its distance is 0; all others are infinity.")
    for iteration in range(max(0, len(nodes) - 1)):
        changed = False
        snapshot(f"Pass {iteration + 1} of {len(nodes) - 1}: inspect every directed version of each link.")
        for u, v, weight in edges:
            if distances[u] != float("inf") and distances[u] + weight < distances[v]:
                old = distances[v]
                distances[v] = distances[u] + weight
                previous[v] = u
                changed = True
                snapshot(
                    f"Relax {u} → {v} (cost {weight}): {format_distance(old)} → {format_distance(distances[v])}.",
                    current=u,
                    explored={u, v},
                )
            else:
                snapshot(f"Check {u} → {v} (cost {weight}): no improvement.", current=u, explored={u, v})
        if not changed:
            snapshot("No distances changed in this pass, so Bellman–Ford can stop early.")
            break
    snapshot("Bellman–Ford finished. The shortest distances have been calculated.")
    return history


def calculate_route(graph, source, destination, algorithm):
    if source not in graph or destination not in graph:
        return None, None
    try:
        if algorithm == "Dijkstra":
            distances, paths = nx.single_source_dijkstra(graph, source, weight="weight")
        else:
            distances, paths = nx.single_source_bellman_ford(graph, source, weight="weight")
        return (distances.get(destination), paths.get(destination))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None, None


# ---------------- NETWORK VISUALIZATION ----------------
def draw_network(graph, route=None, explored=None, current=None, disabled_edge=None):
    route = route or []
    explored = explored or set()
    positions = nx.spring_layout(graph, seed=42, weight="weight")
    fig = go.Figure()

    route_edges = {
        frozenset((route[i], route[i + 1]))
        for i in range(max(0, len(route) - 1))
    }

    # Draw active links and their costs.
    for u, v, data in graph.edges(data=True):
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        on_route = frozenset((u, v)) in route_edges
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color="#16A34A" if on_route else "#94A3B8", width=5 if on_route else 2),
            hoverinfo="text", text=f"{u} ↔ {v}, cost: {data.get('weight', 1)}",
            showlegend=False,
        ))
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=str(data.get("weight", 1)), showarrow=False,
            bgcolor="white", bordercolor="#CBD5E1", borderpad=3,
            font=dict(color="#111827", size=12),
        )

    node_colors = []
    for node in graph.nodes:
        if node == current:
            node_colors.append("#DC2626")
        elif route and node in route:
            node_colors.append("#16A34A")
        elif node in explored:
            node_colors.append("#F59E0B")
        else:
            node_colors.append("#2563EB")

    fig.add_trace(go.Scatter(
        x=[positions[n][0] for n in graph.nodes],
        y=[positions[n][1] for n in graph.nodes],
        mode="markers+text", text=list(graph.nodes), textposition="top center",
        marker=dict(size=36, color=node_colors, line=dict(color="white", width=2)),
        hovertemplate="Router %{text}<extra></extra>", showlegend=False,
    ))
    fig.update_layout(
        height=500, margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False,
    )
    return fig


def distance_table(snapshot, graph_nodes):
    rows = []
    for node in sorted(graph_nodes):
        distance = snapshot["distances"].get(node, float("inf"))
        previous = snapshot["previous"].get(node)
        rows.append({
            "Router": node,
            "Distance from Source": format_distance(distance),
            "Previous Router": previous if previous is not None else ("Source" if distance == 0 else "—"),
            "Status": "Visited / updated" if node in snapshot["explored"] else "Not finalized",
        })
    return pd.DataFrame(rows)


# ---------------- SIDEBAR CONTROLS ----------------
st.sidebar.header("Network Controls")
st.sidebar.subheader("Add Router")
new_router = st.sidebar.text_input("Router name", placeholder="Example: R7")
if st.sidebar.button("Add Router"):
    name = new_router.strip().upper()
    if not name:
        st.sidebar.error("Enter a router name.")
    elif name in G:
        st.sidebar.warning("Router already exists.")
    else:
        G.add_node(name)
        st.session_state.step_index = 0
        st.session_state.step_slider = 0
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("Add Network Link")
routers_for_link = sorted(G.nodes())
if len(routers_for_link) >= 2:
    with st.sidebar.form("add_link_form"):
        source_link = st.selectbox("First router", routers_for_link, key="link_source")
        destination_link = st.selectbox(
            "Second router", routers_for_link,
            index=min(1, len(routers_for_link) - 1), key="link_destination",
        )
        link_cost = st.number_input("Link cost", min_value=1, max_value=1000, value=1)
        add_link = st.form_submit_button("Add / Update Link")
        if add_link:
            if source_link == destination_link:
                st.error("Choose two different routers.")
            else:
                G.add_edge(source_link, destination_link, weight=int(link_cost))
                st.session_state.step_index = 0
                st.session_state.step_slider = 0
                st.rerun()

st.sidebar.divider()
if st.sidebar.button("Reset Sample Network"):
    st.session_state.graph = create_sample_graph()
    st.session_state.step_index = 0
    st.session_state.step_slider = 0
    st.rerun()


# ---------------- ROUTING CONFIGURATION ----------------
st.subheader("Routing Configuration")
left, middle, right = st.columns(3)
routers = sorted(G.nodes())
with left:
    source = st.selectbox("Source Router", routers, key="source_router") if routers else None
with middle:
    destination = st.selectbox(
        "Destination Router", routers,
        index=min(1, len(routers) - 1) if routers else 0,
        key="destination_router",
    ) if routers else None
with right:
    algorithm = st.selectbox("Routing Algorithm", ["Dijkstra", "Bellman-Ford"], key="routing_algorithm")


# ---------------- NETWORK TOPOLOGY ----------------
st.subheader("Network Topology")
st.plotly_chart(draw_network(G), use_container_width=True, key="network_topology")
st.caption("Blue = router | Green = final route | Amber = explored router | Red = current router | Link labels = costs")


if G.number_of_nodes() < 2:
    st.warning("Add at least two routers to run a simulation.")
elif source is not None and destination is not None:
    route_cost, route = calculate_route(G, source, destination, algorithm)
    if route is None:
        st.error(f"No route exists from {source} to {destination}. Try another destination or restore a disabled link.")
    else:
        st.subheader("Routing Results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Selected Route", " → ".join(route))
        c2.metric("Total Route Cost", f"{route_cost:g}")
        start_time = time.perf_counter()
        calculate_route(G, source, destination, algorithm)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        c3.metric("Calculation Time", f"{elapsed_ms:.4f} ms")

        st.plotly_chart(draw_network(G, route=route), use_container_width=True, key="selected_route_graph")
        st.success(f"Best route using {algorithm}: {' → '.join(route)} | Total cost = {route_cost:g}")

        # Routing table for every router reachable from the source.
        if algorithm == "Dijkstra":
            distances, paths = nx.single_source_dijkstra(G, source, weight="weight")
        else:
            distances, paths = nx.single_source_bellman_ford(G, source, weight="weight")
        routing_rows = []
        for target in sorted(G.nodes()):
            if target in paths:
                path = paths[target]
                routing_rows.append({
                    "Destination": target,
                    "Next Hop": path[1] if len(path) > 1 else "Local",
                    "Total Cost": distances[target],
                    "Route": " → ".join(path),
                })
            else:
                routing_rows.append({"Destination": target, "Next Hop": "Unreachable", "Total Cost": "∞", "Route": "No route"})
        st.subheader("Routing Table")
        st.dataframe(pd.DataFrame(routing_rows), use_container_width=True, hide_index=True)

        # ---------------- STEP-BY-STEP NAVIGATION ----------------
        st.divider()
        st.subheader("Step-by-step Routing Walkthrough")
        st.write(f"Algorithm: **{algorithm}** · Source: **{source}** · Destination: **{destination}**")
        history = dijkstra_trace(G, source) if algorithm == "Dijkstra" else bellman_ford_trace(G, source)
        max_step = len(history) - 1
        st.session_state.step_index = max(0, min(st.session_state.step_index, max_step))

        nav1, nav2, nav3 = st.columns([1, 4, 1])
        with nav1:
            if st.button("◀ Previous Step", disabled=st.session_state.step_index <= 0, use_container_width=True):
                st.session_state.step_index -= 1
                st.session_state.step_slider = st.session_state.step_index
                st.rerun()
        with nav3:
            if st.button("Next Step ▶", disabled=st.session_state.step_index >= max_step, use_container_width=True):
                st.session_state.step_index += 1
                st.session_state.step_slider = st.session_state.step_index
                st.rerun()
        with nav2:
            selected_step = st.slider(
                "Recorded algorithm step", min_value=0, max_value=max_step,
                value=st.session_state.step_index, key="step_slider",
                help="Move this slider to inspect each recorded routing operation.",
            )
            st.session_state.step_index = selected_step

        snapshot = history[st.session_state.step_index]
        st.info(f"Step {st.session_state.step_index + 1} of {len(history)}: {snapshot['message']}")
        step_left, step_right = st.columns([1.15, 1])
        with step_left:
            st.plotly_chart(
                draw_network(G, explored=snapshot["explored"], current=snapshot["current"]),
                use_container_width=True,
                key=f"step_graph_{algorithm}_{source}_{st.session_state.step_index}_{G.number_of_edges()}",
            )
        with step_right:
            st.markdown("**Distance table for this step**")
            st.dataframe(distance_table(snapshot, G.nodes()), use_container_width=True, hide_index=True)

        # ---------------- PLAY ANIMATION ----------------
        st.subheader("Play Animation")
        speed = st.slider("Delay between steps (seconds)", min_value=0.1, max_value=1.5, value=0.45, step=0.1, key="animation_speed")
        if st.button("▶ Play Animation from Start", type="primary"):
            graph_slot = st.empty()
            message_slot = st.empty()
            table_slot = st.empty()
            progress = st.progress(0)
            for i, frame in enumerate(history):
                graph_slot.plotly_chart(
                    draw_network(G, explored=frame["explored"], current=frame["current"]),
                    use_container_width=True,
                    key=f"animation_graph_{algorithm}_{i}_{G.number_of_edges()}",
                )
                message_slot.info(f"Animation step {i + 1}/{len(history)}: {frame['message']}")
                table_slot.dataframe(distance_table(frame, G.nodes()), use_container_width=True, hide_index=True)
                progress.progress((i + 1) / len(history))
                time.sleep(speed)
            graph_slot.plotly_chart(draw_network(G, route=route), use_container_width=True, key=f"animation_final_route_{algorithm}_{G.number_of_edges()}")
            message_slot.success(f"Animation complete. Final route: {' → '.join(route)} | Cost: {route_cost:g}")

        # ---------------- ALGORITHM COMPARISON ----------------
        st.divider()
        st.subheader("Dijkstra vs Bellman–Ford")
        st.caption("Both algorithms are run on the same network, source, and destination for a fair comparison.")
        comparison_rows = []
        for algo_name in ["Dijkstra", "Bellman-Ford"]:
            start = time.perf_counter()
            cost, path = calculate_route(G, source, destination, algo_name)
            elapsed = (time.perf_counter() - start) * 1000
            comparison_rows.append({
                "Algorithm": algo_name,
                "Route": " → ".join(path) if path else "No route",
                "Total Cost": f"{cost:g}" if cost is not None else "∞",
                "Calculation Time (ms)": round(elapsed, 5),
                "Result": "Reachable" if path else "Unreachable",
            })
        st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
        if comparison_rows[0]["Route"] == comparison_rows[1]["Route"] and comparison_rows[0]["Total Cost"] == comparison_rows[1]["Total Cost"]:
            st.success("Both algorithms agree on the shortest-path cost and route for this network.")
        elif comparison_rows[0]["Total Cost"] == comparison_rows[1]["Total Cost"]:
            st.info("The algorithms found the same minimum cost. More than one shortest route may exist, so the displayed routes can differ.")
        else:
            st.warning("The algorithms returned different costs. Check the network and link weights.")

        # ---------------- LINK FAILURE SIMULATION ----------------
        st.divider()
        st.subheader("Link Failure Simulation")
        edge_options = [f"{u} — {v} (cost {data.get('weight', 1)})" for u, v, data in G.edges(data=True)]
        if edge_options:
            failed_edge_label = st.selectbox("Choose a link to disable", edge_options, key="failed_link_choice")
            if st.button("Disable Link and Recalculate", type="secondary"):
                # Parse endpoints from the label while allowing router names containing spaces.
                edge_part = failed_edge_label.split(" (cost ", 1)[0]
                u, v = edge_part.split(" — ", 1)
                if G.has_edge(u, v):
                    G.remove_edge(u, v)
                    st.session_state.graph = G
                    st.session_state.step_index = 0
                    st.session_state.step_slider = 0
                    st.session_state.last_failed_link = f"{u} — {v}"
                    st.rerun()
        else:
            st.info("No active links remain to disable.")
        if st.session_state.get("last_failed_link"):
            st.warning(f"Last disabled link: {st.session_state.last_failed_link}. The route and routing table above are recalculated automatically using the remaining active links.")

# ---------------- TESTING CHECKLIST ----------------
st.divider()
st.subheader("Testing Checklist")
st.caption("Tick each item after verifying it in the app.")
checklist_items = [
    "Step-by-step navigation — move the slider and use Previous Step / Next Step.",
    "Play Animation — watch the graph and distance table update through recorded steps.",
    "Dijkstra vs Bellman–Ford — compare both on the same source and destination.",
    "Link failure — disable a link and confirm that the route is recalculated.",
]
for i, item in enumerate(checklist_items):
    st.checkbox(item, key=f"test_check_{i}")
completed = sum(bool(st.session_state.get(f"test_check_{i}", False)) for i in range(len(checklist_items)))
st.progress(completed / len(checklist_items))
st.caption(f"Testing checklist: {completed} of {len(checklist_items)} completed")

# ---------------- NETWORK SUMMARY ----------------
st.divider()
st.subheader("Network Summary")
m1, m2, m3 = st.columns(3)
m1.metric("Total Routers", G.number_of_nodes())
m2.metric("Active Links", G.number_of_edges())
m3.metric("Network Components", nx.number_connected_components(G) if G.number_of_nodes() else 0)
st.caption("Academic simulation only. Routing costs are abstract values, not measured latency.")
