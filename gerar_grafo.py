import os
import pickle
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from tkinter import Tk, filedialog

Tk().withdraw()
root_dir = filedialog.askdirectory(title="Selecione a pasta raiz para o grafo")
if not root_dir:
    print("Nenhuma pasta selecionada. Encerrando.")
    exit()

root_dir = root_dir.replace("\\", "/")
nome_dir = os.path.basename(root_dir.rstrip("/\\")).replace("-", " ").title()

G = nx.Graph()
node_info = {}
max_level = 0

def get_size_kb(path):
    if os.path.isfile(path):
        return os.path.getsize(path) / 1024
    size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                size += os.path.getsize(fp)
    return size / 1024

for folder, subfolders, files in os.walk(root_dir):
    rel_path = os.path.relpath(folder, root_dir).replace("\\", "/").lower()
    folder_name = os.path.basename(folder) or folder
    level = rel_path.count(os.sep)
    max_level = max(max_level, level)
    folder_size = get_size_kb(folder)
    qtd_itens = len(subfolders) + len(files)

    G.add_node(rel_path)
    node_info[rel_path] = {
        "name": folder_name,
        "weight": qtd_itens or 1,
        "level": level,
        "path": folder,
        "tipo": "Diretório",
        "size_kb": folder_size,
        "qtd_itens": qtd_itens
    }

    for subfolder in subfolders:
        subfolder_rel = os.path.relpath(os.path.join(folder, subfolder), root_dir).replace("\\", "/").lower()
        G.add_edge(rel_path, subfolder_rel)

    for file in files:
        file_rel = os.path.relpath(os.path.join(folder, file), root_dir).replace("\\", "/").lower()
        file_path = os.path.join(folder, file)
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
                "level": level + 1,
                "path": file_path,
                "tipo": "Arquivo",
                "size_kb": file_size,
                "qtd_itens": 0
            }

# Garante que todos os nós do G estejam no node_info e pos_3d
for node in G.nodes:
    if node not in node_info:
        node_info[node] = {
            "name": os.path.basename(node),
            "weight": 1,
            "level": 0,
            "path": node,
            "tipo": "Desconhecido",
            "size_kb": 0,
            "qtd_itens": 0
        }

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
        marker=dict(size=np.clip(info["weight"] * 2, 5, 30), color=cor),
        hovertext=f"Nome: {info['name']}<br>Tipo: {info['tipo']}<br>Nível: {info['level']}<br>Tamanho: {info['size_kb']:.2f} KB<br>Qtd Itens: {info['qtd_itens']}",
        hoverinfo="text",
        showlegend=False
    ))

for edge in G.edges:
    x_vals = [pos_3d[edge[0]][0], pos_3d[edge[1]][0]]
    y_vals = [pos_3d[edge[0]][1], pos_3d[edge[1]][1]]
    z_vals = [pos_3d[edge[0]][2], pos_3d[edge[1]][2]]
    fig.add_trace(go.Scatter3d(
        x=x_vals, y=y_vals, z=z_vals, mode="lines",
        line=dict(color="gray", width=1),
        showlegend=False
    ))

with open("grafo_cache.pkl", "wb") as f:
    pickle.dump({"fig": fig, "max_level": max_level}, f)

print("Gráfico salvo como grafo_cache.pkl")