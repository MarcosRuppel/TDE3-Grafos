# TDE3 - Projeto Colaborativo 1
### Disciplina: Resolução de Problemas com Grafos
Grupo: 
- Augusto Trindade Schulze de Sousa
- Enzo Curcio Stival
- Henrique de Oliveira Godoy
- Hiann Wonsowicz Padilha
- Marcos Paulo Ruppel

---

# 📌 Descrição

Este projeto implementa um analisador de contatos baseado no Enron Email Dataset, utilizando grafos direcionados e ponderados, sem o uso de bibliotecas prontas de grafos.

---

# ▶️ Como executar

1. Certifique-se de que a base de dados Enron esteja extraída no diretório desejado.
2. Edite o caminho na linha 298 do arquivo `grafo_enron.py` para apontar para a pasta base dos e-mails.

Exemplo:
```python
caminho_base = "C:/caminho/para/enron_emails"
```

3. Execute:
```bash
python grafo_enron.py
```

---

# 📂 Saídas:
- `lista_adjacencias.txt`: arquivo de texto com a lista de adjacências do grafo.

---

# 🔧 Funcionalidades implementadas:

1. Construção do grafo direcionado ponderado.
2. Informações gerais: número de vértices, arestas, vértices isolados, top 20 de graus.
3. Verificação se o grafo é Euleriano.
4. Consulta de vértices a até uma distância D de um vértice N (via Dijkstra).
5. Cálculo do diâmetro do grafo (maior caminho mínimo).

---

# ❗ Requisitos
- Python 3.x
- Não utiliza bibliotecas de grafos como NetworkX.
