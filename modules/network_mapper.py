import networkx as nx
import plotly.graph_objects as go

def generate_relationship_graph(subject_name: str, github_data: dict, social_data: dict, company: str, breaches: list) -> str:
    """
    Generates an interactive Plotly HTML graph mapping the subject's network.
    Returns the HTML div string for embedding.
    """
    if not subject_name:
        subject_name = "Subject"

    G = nx.Graph()
    G.add_node(subject_name, type="person", color="#0d6efd", size=25)

    # Add Company
    if company:
        G.add_node(company, type="company", color="#198754", size=20)
        G.add_edge(subject_name, company, label="Works At")

    # Add Github
    if github_data and isinstance(github_data, dict) and github_data.get("username"):
        gh_user = github_data.get("username")
        G.add_node(gh_user, type="github", color="#212529", size=15)
        G.add_edge(subject_name, gh_user, label="Owns Github")

    # Add Social
    if social_data and isinstance(social_data, dict):
        for platform, profile in social_data.items():
            if profile:
                G.add_node(f"{platform}_profile", type="social", color="#0dcaf0", size=15)
                G.add_edge(subject_name, f"{platform}_profile", label=f"On {platform}")

    # Add Breaches
    if breaches and isinstance(breaches, list):
        for breach in breaches:
            G.add_node(breach, type="breach", color="#dc3545", size=15)
            G.add_edge(subject_name, breach, label="Exposed In")

    # Generate layout
    try:
        pos = nx.spring_layout(G, seed=42)
    except Exception:
        pos = nx.random_layout(G)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_color.append(G.nodes[node]['color'])
        node_size.append(G.nodes[node]['size'])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="bottom center",
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title=dict(
                    text='',
                    font=dict(size=16)
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

    # Return as an HTML div without full html/head/body tags
    return fig.to_html(full_html=False, include_plotlyjs='cdn')
