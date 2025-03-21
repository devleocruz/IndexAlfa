# Projeto Indexalfa - Visualização 3D de Estrutura de Diretórios

## Objetivo
Desenvolver um sistema de visualização interativa 3D que mapeia a estrutura de diretórios e arquivos de um diretório raiz selecionado. O projeto é dividido em duas partes principais: **geração do grafo** e **visualização via aplicativo Dash**.

---

## Componentes principais

### 1) **`gerar_grafo.py`**
- Responsável por percorrer uma pasta selecionada no sistema de arquivos.
- Cria um grafo usando **NetworkX**, registrando **pastas** e **arquivos**.
- Calcula:
  - Quantidade de itens por pasta
  - Tamanho em KB
  - Nível de profundidade
- Gera um grafo 3D usando **Plotly**.
- As cores dos nós seguem um gradiente controlado baseado no nível de profundidade:
  - Azul → Roxo → Violeta → Verde → Vermelho claro → Vermelho quente.
- O grafo e metadados são salvos em um **pickle (`grafo_cache.pkl`)**.

### 2) **`app_dash.py`**
- Carrega o `grafo_cache.pkl` e exibe o grafo em um dashboard com **Dash + Plotly**.
- O layout é dividido em duas colunas:
  - **92% para o mapa 3D** (esquerda)
  - **8% para o painel lateral** com dropdown e legenda dinâmica.
- Funções no painel lateral:
  - Selecionar a métrica de dimensionamento dos nós (**Qtd de Itens** ou **Tamanho em KB**).
  - Exibir legenda adaptativa com as cores por nível.

---

## Outras características
- O app Dash remove todos os eixos, grids e planos de fundo.
- Hovertext exibe dados resumidos do nó: nome, tipo, nível, tamanho e quantidade de itens.
- O grafo é processado e salvo já com as cores definitivas (não há "piscada" de cor ao abrir o app).
- O projeto foi projetado para **rodar localmente** via Python e Dash.

## Público
Desenvolvido para a **Alfa Contabilidade** por Leonardo Cruz e Gabriel Inácio, no contexto do **Projeto Indexalfa 2025**.

---

## Tecnologias
- **Python**
- **Dash** (Plotly)
- **NetworkX**
- **Tkinter** (para selecionar a pasta via GUI)

---

> Observação: Caso o novo analista ou chatbot precise de mais detalhes sobre regras de negócio, métricas ou integrações futuras, é só me consultar!

---
