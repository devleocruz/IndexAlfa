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

1. Execute o gerador:
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
