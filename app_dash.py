import pickle
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import os

# Carrega pickle já com cores corretas
with open("grafo_cache.pkl", "rb") as f:
    data = pickle.load(f)
    fig_base = data["fig"]
    max_level = data["max_level"]

app = dash.Dash(__name__)

# Ajuste global da cena
fig_base.update_layout(
    scene=dict(
        xaxis=dict(visible=False, backgroundcolor='rgba(0,0,0,0)'),
        yaxis=dict(visible=False, backgroundcolor='rgba(0,0,0,0)'),
        zaxis=dict(visible=False, backgroundcolor='rgba(0,0,0,0)')
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

def gradiente_rgb(level, max_level=20):
    pct = level / max(max_level, 1)
    if pct < 0.2: return '#1E90FF'
    elif pct < 0.4: return '#6A5ACD'
    elif pct < 0.55: return '#8A2BE2'
    elif pct < 0.7: return '#32CD32'
    elif pct < 0.85: return '#FF7F7F'
    else: return '#FF0000'

def gerar_legenda(max_level):
    return [
        html.Div([
            html.Span(style={'display': 'inline-block', 'width': '10px', 'height': '10px',
                             'backgroundColor': gradiente_rgb(lvl, max_level),
                             'borderRadius': '50%', 'marginRight': '5px'}),
            html.Span(f'Nível {lvl}')
        ], style={"fontSize": "10px", "marginBottom": "4px"})
        for lvl in range(max_level + 1)
    ]

app.layout = html.Div([
    html.H3("Mapa 3D da Estrutura de Diretórios", style={"margin": "2px 0", "textAlign": "center", "fontSize": "18px"}),

    html.Div([
        html.Div([
            dcc.Graph(
                id="grafo",
                figure=fig_base,
                config={"displayModeBar": False},
                style={"height": "96vh", "width": "100%"}
            )
        ], style={"width": "92%", "display": "inline-block", "verticalAlign": "top", "padding": "0"}),

        html.Div([
            dcc.Dropdown(
                id="dimensao",
                options=[
                    {"label": "Qtd de Itens", "value": "qtd"},
                    {"label": "Tamanho em KB", "value": "kb"}
                ],
                value="qtd",
                clearable=False,
                style={"width": "90%", "fontSize": "12px", "marginBottom": "10px"}
            ),
            html.Div(
                gerar_legenda(max_level),
                id="legenda-niveis",
                style={"paddingLeft": "5px"}
            )
        ], style={"width": "8%", "display": "inline-block", "verticalAlign": "top", "paddingTop": "5px"}),
    ], style={"width": "100%", "display": "flex"}),

    html.Div(
        "Desenvolvido por Leonardo Cruz e Gabriel Inácio - Projeto Indexalfa 2025 | Alfa Contabilidade",
        style={"textAlign": "center", "color": "gray", "fontSize": "12px", "marginTop": "2px"}
    )
])

@app.callback(
    Output("grafo", "figure"),
    Input("dimensao", "value")
)
def update_graph(dimensao):
    fig = go.Figure(fig_base)
    for trace in fig.data:
        if trace.mode == "markers":
            trace.marker.size = min(15, trace.marker.size or 10) if dimensao == "qtd" else min(25, (trace.marker.size or 10) * 1.5)
    return fig

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)
