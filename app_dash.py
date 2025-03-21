import pickle
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import os

# Carrega pickle já com o root_name
with open("grafo_cache.pkl", "rb") as f:
    data = pickle.load(f)
    fig_base = data["fig"]
    max_level = data["max_level"]
    root_name = data.get("root_name", "Diretórios")

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

def gerar_legenda(max_level):
    cores = ['#1E90FF', '#6A5ACD', '#8A2BE2', '#32CD32', '#FF7F7F', '#FF0000']
    return [
        html.Div([
            html.Span(style={'display': 'inline-block', 'width': '15px', 'height': '15px',
                             'backgroundColor': cores[min(int(lvl * len(cores) / max(max_level, 1)), len(cores)-1)],
                             'borderRadius': '50%', 'marginRight': '8px'}),
            html.Span(f'Nível {lvl}', style={"fontSize": "12px"})
        ], style={"marginBottom": "6px"})
        for lvl in range(max_level + 1)
    ]

app.layout = html.Div([
    html.H3(f"Representação Tridimensional - {root_name}", style={"margin": "2px 0", "textAlign": "center", "fontSize": "18px"}),

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
                style={"width": "90%", "fontSize": "14px", "marginBottom": "15px"}
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

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)