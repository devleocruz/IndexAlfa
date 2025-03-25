import pickle
import dash
from dash import dcc, html
import plotly.graph_objects as go
import numpy as np

with open("grafo_cache.pkl", "rb") as f:
    data = pickle.load(f)
    max_level = data["max_level"]
    root_name = data.get("root_name", "Diretórios")
    G = data["graph"]
    node_info = data["node_info"]

np.random.seed(42)
pos_2d = {}
for node, info in node_info.items():
    lvl = info["level"]
    x = lvl * 50
    y = np.random.uniform(-20 * (lvl + 1), 20 * (lvl + 1))
    pos_2d[node] = (x, y)

def gradiente_rgb(level):
    pct = level / max(max_level, 1)
    if pct < 0.2: return '#1E90FF'
    elif pct < 0.4: return '#6A5ACD'
    elif pct < 0.55: return '#8A2BE2'
    elif pct < 0.7: return '#32CD32'
    elif pct < 0.85: return '#FF7F7F'
    else: return '#FF0000'

fig_2d = go.Figure()

for edge in G.edges():
    if edge[0] in pos_2d and edge[1] in pos_2d:
        x0, y0 = pos_2d[edge[0]]
        x1, y1 = pos_2d[edge[1]]
        fig_2d.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color="gray", width=1),
            showlegend=False
        ))

for node, (x, y) in pos_2d.items():
    info = node_info[node]
    fig_2d.add_trace(go.Scatter(
        x=[x], y=[y],
        mode="markers",
        marker=dict(
            size=np.clip(info["weight"] * 2, 5, 30),
            color=gradiente_rgb(info["level"])
        ),
        hovertext=(
            f"Nome: {info['name']}<br>"
            f"Tipo: {info['tipo']}<br>"
            f"Nível: {info['level']}<br>"
            f"Tamanho: {info['size_kb']:.2f} KB<br>"
            f"Qtd Itens: {info['qtd_itens']}"
        ),
        hoverinfo="text",
        showlegend=False
    ))

fig_2d.update_layout(
    title=dict(
        text=f"Representação Bidimensional - {root_name}",
        x=0.5,
        xanchor="center",
        font=dict(size=18)
    ),
    margin=dict(l=0, r=0, b=60, t=40),
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    annotations=[
        dict(
            text="Desenvolvido por Leonardo Cruz e Gabriel Inácio - Projeto Indexalfa 2025 | Alfa Contabilidade",
            x=0.5, y=0, xref='paper', yref='paper',
            showarrow=False, font=dict(size=12, color="gray"), xanchor='center', yanchor='bottom'
        )
    ]
)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H3(f"Representação Bidimensional - {root_name}", style={"margin": "2px 0", "textAlign": "center", "fontSize": "18px"}),

    html.Div([
        html.Div([
            dcc.Graph(
                id="grafo-2d",
                figure=fig_2d,
                config={"displayModeBar": False},
                style={"height": "96vh", "width": "100%"}
            )
        ], style={"width": "100%", "display": "inline-block"})
    ])
])

if __name__ == "__main__":
    app.run(debug=True)