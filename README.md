# Projeto Indexalfa - Visualização Interativa de Estrutura de Diretórios

## Objetivo
Desenvolver um sistema de visualização interativa (2D e 3D) para mapear estruturas de diretórios e arquivos, com base na quantidade de itens ou tamanho em KB. A visualização é responsiva e adaptada para exploração local via navegador.

---

## Componentes principais

### 1) `gerar_grafo.py`
- **Interface Tkinter** para configurar os filtros de mapeamento:
  - Pasta raiz
  - Tipo de conteúdo: `Todo conteúdo` ou `Somente pastas`
  - Nível máximo de profundidade
- Percorre a árvore de diretórios e arquivos, coletando:
  - Nível de profundidade
  - Quantidade de itens
  - Tamanho em KB
- Gera um grafo usando `NetworkX` e salva os dados e o layout 3D em um arquivo `grafo_cache.pkl`.
- Cores dos nós baseadas no nível de profundidade.
- Processamento rápido, mesmo com estruturas extensas (multi-nível).
- Pode ser executado independentemente com `python gerar_grafo.py`.

---

### 2) `app_dash.py`
- Lê o `grafo_cache.pkl` gerado anteriormente.
- Renderiza um dashboard com **Dash + Plotly**, oferecendo:
  - **Dropdowns** para seleção do tipo de visualização: `2D` ou `3D`
  - **Métrica de dimensionamento**: `Qtd de Itens` ou `Tamanho em KB`
  - Legenda de níveis dinâmica (cor e nome)
- Layout dividido:
  - **90%** para o grafo
  - **10%** para painel de controle lateral
- Grafo interativo com hover personalizado contendo:
  - Nome do arquivo/pasta
  - Tipo (Arquivo/Diretório)
  - Nível, tamanho (KB), quantidade de itens
- Responsivo e adaptável à janela do navegador.

---

## Tecnologias Utilizadas
- **Python**
- **Dash** / **Plotly**
- **NetworkX**
- **Tkinter**

---

## Nível de Dificuldade

| Aspecto                        | Nível       | Observações |
|-------------------------------|-------------|-------------|
| Processamento de diretórios   | 🟡 Intermediário | Usa recursão e tratamento de caminhos relativos |
| Geração de gráficos com Plotly| 🔵 Avançado      | Requer conhecimento de layout 2D/3D e configuração de traces |
| Interface com Dash            | 🟡 Intermediário | Integração com callbacks, dropdowns e gráficos interativos |
| Interface com Tkinter         | 🟢 Básico        | Janela de entrada com campos e validação simples |
| Performance com grandes estruturas | 🔵 Avançado | Otimizações com cache, clipping de tamanhos, posicionamento por nível |

---

## Tratamento de Erros

| Possível erro | Causa | Tratamento |
|---------------|-------|------------|
| **`Selecione uma pasta primeiro.`** | Usuário clicou em OK sem selecionar pasta | Exibição de popup com `messagebox.showerror` |
| **`Digite um número válido para o nível máximo.`** | Campo de nível está vazio ou com texto inválido | Validação com try/except e popup |
| **`FileNotFoundError` ao acessar arquivos** | Arquivo foi movido ou está inacessível durante o mapeamento | Tratado com `try/except` e valor 0 como fallback |
| **`len(file_path) >= 260`** | Caminho muito longo no Windows | Esses arquivos são ignorados |
| **Arquivo `grafo_cache.pkl` não encontrado** | O `app_dash.py` foi executado sem gerar o grafo antes | Recomenda-se rodar o `gerar_grafo.py` antes |
| **Visualização com layout corrompido** | Alterações manuais no arquivo `.pkl` ou estrutura muito irregular | Recomenda-se reexecutar o mapeamento com parâmetros mais simples |

---

## Execução

#### 1) Para exeutar você precisa de três aquivos:
1. `requirements.txt`
```bash
altgraph==0.17.4
blinker==1.9.0
certifi==2025.1.31
charset-normalizer==3.4.1
click==8.1.8
colorama==0.4.6
contourpy==1.3.1
cycler==0.12.1
dash==3.0.0
Flask==3.0.3
fonttools==4.56.0
idna==3.10
importlib_metadata==8.6.1
itsdangerous==2.2.0
Jinja2==3.1.6
kiwisolver==1.4.8
MarkupSafe==3.0.2
matplotlib==3.10.1
narwhals==1.31.0
nest-asyncio==1.6.0
networkx==3.4.2
numpy==2.2.4
packaging==24.2
pefile==2023.2.7
pillow==11.1.0
plotly==6.0.1
pyinstaller==6.12.0
pyinstaller-hooks-contrib==2025.1
pyparsing==3.2.1
python-dateutil==2.9.0.post0
pywin32-ctypes==0.2.3
requests==2.32.3
retrying==1.3.4
scipy==1.15.2
six==1.17.0
stringcase==1.2.0
typing_extensions==4.12.2
urllib3==2.3.0
Werkzeug==3.0.6
zipp==3.21.0
```

2. `gerar_grafo.py`
```python
import os
import pickle
import networkx as nx
import numpy as np
import plotly.graph_objects as go
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

"""---------------- INTERFACE ------------------"""
class FiltroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtros de Mapeamento")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Tipo de conteúdo
        ttk.Label(root, text="Conteúdo a mapear:").pack(pady=5)
        self.tipo_var = tk.StringVar(value="Todo conteúdo")
        self.tipo_dropdown = ttk.Combobox(root, textvariable=self.tipo_var, state="readonly")
        self.tipo_dropdown['values'] = ("Todo conteúdo", "Somente pastas")
        self.tipo_dropdown.pack()

        # Nível máximo (campo livre)
        ttk.Label(root, text="Nível máximo de mapeamento:").pack(pady=5)
        self.nivel_var = tk.StringVar()
        self.nivel_entry = ttk.Entry(root, textvariable=self.nivel_var)
        self.nivel_entry.pack()

        # Seletor de pasta com campo e botão lado a lado
        pasta_frame = ttk.Frame(root)
        pasta_frame.pack(pady=10, fill="x", padx=20)

        self.pasta_entry = ttk.Entry(pasta_frame, textvariable=tk.StringVar(), state="readonly")
        self.pasta_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(pasta_frame, text="Selecionar", command=self.selecionar_pasta).pack(side="left", padx=5)

        # Label de status
        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)

        # Botões finais
        frame_botoes = ttk.Frame(root)
        frame_botoes.pack(pady=30)
        self.botao_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=root.destroy)
        self.botao_cancelar.pack(side="left", padx=20)
        self.botao_ok = ttk.Button(frame_botoes, text="OK", command=self.iniciar_mapeamento)
        self.botao_ok.pack(side="right", padx=20)

        self.pasta_var = ""

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta raiz")
        if pasta:
            self.pasta_var = pasta
            encurtado = self.encurtar_caminho(pasta)
            self.pasta_entry.config(state="normal")
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, encurtado)
            self.pasta_entry.config(state="readonly")

    def encurtar_caminho(self, caminho, limite=60):
        caminho = caminho.replace("\\", "/")
        return caminho if len(caminho) <= limite else "..." + caminho[-limite:]

    def iniciar_mapeamento(self):
        pasta = self.pasta_var
        if not pasta:
            messagebox.showerror("Erro", "Selecione uma pasta primeiro.")
            return

        tipo = self.tipo_var.get()
        try:
            nivel_max = int(self.nivel_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido para o nível máximo.")
            return

        self.status_label.config(text="Mapeando...")
        self.botao_ok.config(state="disabled")

        threading.Thread(target=self.executar_mapeamento, args=(pasta, tipo, nivel_max), daemon=True).start()

    def executar_mapeamento(self, pasta, tipo, nivel):
        gerar_grafo(pasta, tipo, nivel)
        self.status_label.config(text="Mapeamento finalizado! (grafo_cache.pkl)")
        self.botao_ok.config(state="normal")

"""-------------- FUNÇÃO DE GERAÇÃO DO GRAFO -------------------"""
def gerar_grafo(root_dir, tipo_conteudo, nivel_max_user):
    root_dir = root_dir.replace("\\", "/")
    nome_dir = os.path.basename(root_dir.rstrip("/\\")).replace("-", " ")

    G = nx.Graph()
    node_info = {}
    max_level = 0

    def get_size_kb(path):
        if os.path.isfile(path):
            return os.path.getsize(path) / 1024
        size = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    size += entry.stat().st_size
        except Exception:
            pass
        return size / 1024


    def caminhar_pasta(pasta_atual, nivel):
        nonlocal max_level
        if nivel > nivel_max_user:
            return

        rel_path = os.path.relpath(pasta_atual, root_dir).replace("\\", "/")
        folder_name = os.path.basename(pasta_atual) or pasta_atual
        folder_size = get_size_kb(pasta_atual)

        try:
            subdirs = [d for d in os.listdir(pasta_atual) if os.path.isdir(os.path.join(pasta_atual, d))]
            files = [f for f in os.listdir(pasta_atual) if os.path.isfile(os.path.join(pasta_atual, f))]
        except Exception:
            subdirs, files = [], []

        qtd_itens = len(subdirs) + len(files)
        max_level = max(max_level, nivel)

        G.add_node(rel_path)
        node_info[rel_path] = {
            "name": folder_name,
            "weight": qtd_itens or 1,
            "level": nivel,
            "path": pasta_atual,
            "tipo": "Diretório",
            "size_kb": folder_size,
            "qtd_itens": qtd_itens
        }

        for subfolder in subdirs:
            sub_path = os.path.join(pasta_atual, subfolder)
            sub_rel = os.path.relpath(sub_path, root_dir).replace("\\", "/")
            G.add_edge(rel_path, sub_rel)
            caminhar_pasta(sub_path, nivel + 1)

        if tipo_conteudo == "Todo conteúdo":
            for file in files:
                file_path = os.path.join(pasta_atual, file)
                file_rel = os.path.relpath(file_path, root_dir).replace("\\", "/")
                if nivel + 1 > nivel_max_user:
                    continue
                if os.path.exists(file_path):
                    try:
                        file_size = os.path.getsize(file_path) / 1024
                    except FileNotFoundError:
                        file_size = 0
                    G.add_node(file_rel)
                    G.add_edge(rel_path, file_rel)
                    node_info[file_rel] = {
                        "name": file,
                        "weight": 1,
                        "level": nivel + 1,
                        "path": file_path,
                        "tipo": "Arquivo",
                        "size_kb": file_size,
                        "qtd_itens": 0
                    }

    caminhar_pasta(root_dir, nivel=0)

    # Layout e visualização
    np.random.seed(42)
    pos_3d = {node: np.array([
        np.random.uniform(-10, 10),
        np.random.uniform(-10, 10),
        node_info[node]['level'] * 20
    ]) for node in node_info}

    def gradiente_rgb(level, max_level=20):
        pct = level / max(max_level, 1)
        if pct < 0.2: return '#1E90FF'
        elif pct < 0.4: return '#6A5ACD'
        elif pct < 0.55: return '#8A2BE2'
        elif pct < 0.7: return '#32CD32'
        elif pct < 0.85: return '#FF7F7F'
        else: return '#FF0000'

    fig = go.Figure()

    for node, coord in pos_3d.items():
        info = node_info[node]
        cor = gradiente_rgb(info["level"], max_level)
        fig.add_trace(go.Scatter3d(
            x=[coord[0]], y=[coord[1]], z=[coord[2]],
            mode="markers",
            marker=dict(size=np.clip(info["weight"] * 1.5, 4, 15), color=cor),
            hovertext=f"Nome: {info['name']}<br>Tipo: {info['tipo']}<br>Nível: {info['level']}<br>Tamanho: {info['size_kb']:.2f} KB<br>Qtd Itens: {info['qtd_itens']}",
            hoverinfo="text",
            showlegend=False
        ))

    for edge in G.edges:
        if edge[0] in pos_3d and edge[1] in pos_3d:
            x_vals = [pos_3d[edge[0]][0], pos_3d[edge[1]][0]]
            y_vals = [pos_3d[edge[0]][1], pos_3d[edge[1]][1]]
            z_vals = [pos_3d[edge[0]][2], pos_3d[edge[1]][2]]
            fig.add_trace(go.Scatter3d(
                x=x_vals, y=y_vals, z=z_vals, mode="lines",
                line=dict(color="gray", width=1),
                showlegend=False
            ))

    with open("grafo_cache.pkl", "wb") as f:
        pickle.dump({
            "fig": fig,
            "max_level": max_level,
            "root_name": nome_dir,
            "graph": G,
            "node_info": node_info
        }, f)

    print("Gráfico salvo como grafo_cache.pkl")

"""----------------- EXECUÇÃO --------------------"""
if __name__ == "__main__":
    root = tk.Tk()
    app = FiltroApp(root)
    root.mainloop()
```

3. `app_dash.py`
```python
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
        size = np.clip(size * 1.5, 5, 25)

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
    app.run(debug=True) # Para executar localmente
```

#### 2) Configurando o ambiente virtual:
1. Criar um novo ambiente virtual
```bash
python -m venv venv
.env\Scripts\Activate
```

2. Instalar as dependências:
```bash
pip install -r requirements.txt
```

O pip vai instalar exatamente as mesmas versões das bibliotecas usadas no projeto.

---


#### 3) Executando:
1. Execute o gerador
```bash
python gerar_grafo.py
```

2. Após gerar o `grafo_cache.pkl`, inicie a visualização:
```bash
python app_dash.py
```

A aplicação será iniciada localmente no endereço: [http://localhost:8050](http://localhost:8050)

---

## Autores
Desenvolvido por **Leonardo Cruz** e **Gabriel Inácio**  
**Projeto Indexalfa 2025** | Alfa Contabilidade

---
