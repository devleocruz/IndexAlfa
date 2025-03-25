import os
import pickle
import networkx as nx
import numpy as np
import plotly.graph_objects as go
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# ---------------- INTERFACE ------------------
class FiltroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtros de Mapeamento")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.iconbitmap("icone.ico")


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

# -------------- FUNÇÃO DE GERAÇÃO DO GRAFO -------------------
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

# ----------------- EXECUÇÃO --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FiltroApp(root)
    root.mainloop()