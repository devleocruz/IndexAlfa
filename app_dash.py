import pickle
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
import os

# Carrega o grafo
with open("grafo_cache.pkl", "rb") as f:
    data = pickle.load(f)

G = data["graph"]
node_info = data["node_info"]
max_level = data["max_level"]
root_name = data.get("root_name", "Diretórios")

# Inicializa o app
app = dash.Dash(__name__)

# Função para gerar cores por nível
def gradiente_rgb(level):
    pct = level / max(max_level, 1)
    if pct < 0.2: return '#1E90FF'
    elif pct < 0.4: return '#6A5ACD'
    elif pct < 0.55: return '#8A2BE2'
    elif pct < 0.7: return '#32CD32'
    elif pct < 0.85: return '#FF7F7F'
    else: return '#FF0000'

# Gera layout base
def gerar_layout():
    return html.Div([
        html.H3(f"Visualização da Estrutura - {root_name}", style={"textAlign": "center", "margin": "5px", "fontSize": "18px"}),

        html.Div([
            html.Div([
                dcc.Graph(
                    id="grafo",
                    config={"displayModeBar": False},
                    style={"height": "95vh", "width": "100%"}
                )
            ], style={"width": "90%"}),

            html.Div([
                dcc.Dropdown(
                    id="modo",
                    options=[
                        {"label": "2D", "value": "2d"},
                        {"label": "3D", "value": "3d"},
                    ],
                    value="3d",
                    clearable=False,
                    style={"fontSize": "14px", "marginBottom": "8px"}
                ),
                dcc.Dropdown(
                    id="dimensao",
                    options=[
                        {"label": "Qtd de Itens", "value": "qtd"},
                        {"label": "Tamanho em KB", "value": "kb"},
                    ],
                    value="qtd",
                    clearable=False,
                    style={"fontSize": "14px"}
                ),
                html.Div(id="legenda-niveis", style={"marginTop": "20px"})
            ], style={"width": "10%", "padding": "10px", "verticalAlign": "top"})

        ], style={"display": "flex", "width": "100%"}),

        html.Div("Desenvolvido por Leonardo Cruz e Gabriel Inácio - Projeto Indexalfa 2025 | Alfa Contabilidade",
                 style={"textAlign": "center", "color": "gray", "fontSize": "12px", "marginTop": "5px"})
    ])

# Gera as legendas dinâmicas
def gerar_legenda(max_level):
    cores = [gradiente_rgb(lvl) for lvl in range(max_level + 1)]
    return [
        html.Div([
            html.Span(style={"display": "inline-block", "width": "15px", "height": "15px",
                             "backgroundColor": cor, "borderRadius": "50%", "marginRight": "6px"}),
            html.Span(f"Nível {lvl}", style={"fontSize": "12px"})
        ], style={"marginBottom": "5px"}) for lvl, cor in enumerate(cores)
    ]

# Callback principal
@app.callback(
    Output("grafo", "figure"),
    Output("legenda-niveis", "children"),
    Input("modo", "value"),
    Input("dimensao", "value")
)
def atualizar_grafo(modo, dimensao):
    fig = go.Figure()

    # Posições
    np.random.seed(42)
    pos = {}
    for node, info in node_info.items():
        lvl = info["level"]
        if modo == "2d":
            x = lvl * 50
            y = np.random.uniform(-20 * (lvl + 1), 20 * (lvl + 1))
            pos[node] = (x, y)
        else:
            x = np.random.uniform(-10, 10)
            y = np.random.uniform(-10, 10)
            z = lvl * 20
            pos[node] = (x, y, z)

    # Arestas
    for edge in G.edges():
        if edge[0] in pos and edge[1] in pos:
            if modo == "2d":
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines",
                                         line=dict(color="gray", width=1), showlegend=False))
            else:
                x0, y0, z0 = pos[edge[0]]
                x1, y1, z1 = pos[edge[1]]
                fig.add_trace(go.Scatter3d(x=[x0, x1], y=[y0, y1], z=[z0, z1], mode="lines",
                                           line=dict(color="gray", width=1), showlegend=False))

    # Nós
    for node, info in node_info.items():
        cor = gradiente_rgb(info["level"])
        size = info["qtd_itens"] if dimensao == "qtd" else info["size_kb"]
        size = np.clip(size * 1.5, 5, 20)

        texto = f"Nome: {info['name']}<br>Tipo: {info['tipo']}<br>Nível: {info['level']}<br>Tamanho: {info['size_kb']:.2f} KB<br>Qtd Itens: {info['qtd_itens']}"

        if modo == "2d":
            x, y = pos[node]
            fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers",
                                     marker=dict(size=size, color=cor), hovertext=texto, hoverinfo="text", showlegend=False))
        else:
            x, y, z = pos[node]
            fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode="markers",
                                       marker=dict(size=size, color=cor), hovertext=texto, hoverinfo="text", showlegend=False))

    # Layout final
    layout = dict(
        margin=dict(l=0, r=0, b=30, t=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    if modo == "3d":
        layout["scene"] = dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        )
        fig.update_layout(**layout)
    else:
        layout["xaxis"] = dict(visible=False)
        layout["yaxis"] = dict(visible=False)
        fig.update_layout(**layout)

    return fig, gerar_legenda(max_level)

app.layout = gerar_layout()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))

    app.run(host="0.0.0.0", port=port, debug=True) 
    # app.run(debug=True) # Para executar localmente

