# grafo_enron.py
# Projeto TDE3 - Analisador de contatos via grafos com base no Enron Email Dataset
# Autor(es):
# - Augusto Trindade Schulze de Sousa
# - Enzo Curcio Stival
# - Henrique de Oliveira Godoy
# - Hiann Wonsowicz Padilha
# - Marcos Paulo Ruppel
# Descrição: Implementação de um grafo direcionado e ponderado para análise de e-mails da Enron,
# incluindo funcionalidades como grau dos vértices, checagem de ciclo euleriano, busca por distância e diâmetro do grafo.

import os
import re
import heapq
from collections import defaultdict, deque
from email.utils import parseaddr, getaddresses

class GrafoEnron:
    def __init__(self):
        # Estrutura de grafo: {remetente: {destinatário: peso}}
        self.grafo = defaultdict(dict)
        self.vertices = set()

    def processar_emails(self, caminho_base):
        """
        Constrói o grafo lendo todos os e-mails contidos no diretório informado.
        Cada remetente é conectado a seus destinatários por uma aresta ponderada,
        onde o peso representa a quantidade de e-mails enviados.
        """
        for root, _, files in os.walk(caminho_base):
            for file in files:
                caminho_arquivo = os.path.join(root, file)
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                        conteudo = f.read()
                        remetente = self._extrair_remetente(conteudo)
                        destinatarios = self._extrair_destinatarios(conteudo)
                        if remetente and destinatarios:
                            for destinatario in destinatarios:
                                self._adicionar_aresta(remetente, destinatario)
                except Exception:
                    continue


    def _extrair_remetente(self, conteudo):
        """
        Extrai o e-mail do remetente utilizando `parseaddr` do módulo `email.utils`.

        Retorna:
        str ou None: Endereço de e-mail em minúsculas, ou None se não encontrado.
        """
        match = re.search(r"^From:\s*(.+)$", conteudo, re.MULTILINE | re.IGNORECASE)
        if match:
            nome, endereco = parseaddr(match.group(1))
            if endereco:
                return endereco.lower()
        return None

    def _extrair_destinatarios(self, conteudo):
        """
        Extrai todos os e-mails dos campos 'To:' do conteúdo do e-mail, incluindo múltiplas linhas.

        Retorna:
        list[str]: Lista de e-mails normalizados.
        """
        padrao = re.compile(r"^To:\s*(.+(?:\n[ \t].+)*)", re.IGNORECASE | re.MULTILINE)
        match = padrao.search(conteudo)
        if match:
            texto_completo = match.group(1).replace('\n', ' ')
            enderecos = getaddresses([texto_completo])
            return [email.lower() for _, email in enderecos if email]
        return []

    def _adicionar_aresta(self, de, para):
        """
        Adiciona uma aresta direcionada entre dois e-mails no grafo, ou incrementa seu peso.

        Parâmetros:
        de (str): E-mail do remetente.
        para (str): E-mail do destinatário.
        """
        if para == de:
            return
        self.vertices.update([de, para])
        if para in self.grafo[de]:
            self.grafo[de][para] += 1
        else:
            self.grafo[de][para] = 1
        if para not in self.grafo:
            self.grafo[para] = {}

    def salvar_lista_adjacencias(self, caminho_saida):
        """
        Salva a lista de adjacência do grafo em um arquivo de texto.

        Cada linha do arquivo terá o formato:
        remetente -> destinatário [peso: número de mensagens enviadas]
        """
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            for de in self.grafo:
                for para in self.grafo[de]:
                    peso = self.grafo[de][para]
                    f.write(f"{de} -> {para} [peso: {peso}]\n")

    def numero_de_vertices(self):
        """
        Retorna o número total de vértices (endereços de e-mail únicos) no grafo.

        Retorna:
        int: Número de vértices.
        """
        return len(self.vertices)

    def numero_de_arestas(self):
        """
        Retorna o número total de arestas únicas no grafo.

        Cada par remetente-destinatário é contado apenas uma vez,
        independentemente do número de mensagens trocadas (peso).
        """
        return sum(len(destinatarios) for destinatarios in self.grafo.values())


    def vertices_isolados(self):
        """
        Conta os vértices isolados, que não têm nenhuma aresta de entrada ou saída.

        Retorna:
        int: Número de vértices isolados.
        """
        grau_entrada = defaultdict(int)
        for origem in self.grafo:
            for destino in self.grafo[origem]:
                grau_entrada[destino] += 1
        isolados = [v for v in self.vertices if len(self.grafo.get(v, {})) == 0 and grau_entrada[v] == 0]
        return len(isolados)

    def top_20_grau_saida(self):
        """
        Retorna os 20 vértices com maior grau de saída (mais mensagens enviadas).

        Retorna:
        list[tuple[int, str]]: Lista com tuplas (grau de saída, e-mail), ordenada de forma decrescente.
        """
        graus = [(sum(self.grafo[v].values()), v) for v in self.grafo]
        return sorted(graus, reverse=True)[:20]

    def top_20_grau_entrada(self):
        """
        Retorna os 20 vértices com maior grau de entrada (mais mensagens recebidas).

        Retorna:
        list[tuple[int, str]]: Lista com tuplas (grau de entrada, e-mail), ordenada de forma decrescente.
        """
        graus = defaultdict(int)
        for origem in self.grafo:
            for destino, peso in self.grafo[origem].items():
                graus[destino] += peso
        return sorted([(grau, v) for v, grau in graus.items()], reverse=True)[:20]


    def grafo_euleriano(self):
        """
        Verifica se o grafo é Euleriano (possui um ciclo que percorre todas as arestas exatamente uma vez).

        Para ser Euleriano:
        - Todos os vértices devem ter grau de entrada igual ao grau de saída.
        - O grafo deve ser fortemente conexo.

        Retorna:
        tuple[bool, list[str]]: (True se é Euleriano, False caso contrário; lista de motivos se não for)
        """
        problemas = []
        grau_entrada = defaultdict(int)

        for origem in self.grafo:
            for destino in self.grafo[origem]:
                grau_entrada[destino] += self.grafo[origem][destino]

        inconsistencias = []
        for v in self.vertices:
            saida = sum(self.grafo[v].values()) if v in self.grafo else 0
            entrada = grau_entrada[v]
            if entrada != saida:
                inconsistencias.append(f"   - {v} → entrada: {entrada}, saída: {saida}")

        if inconsistencias:
            problemas.append("❌ Grau de entrada ≠ grau de saída em alguns vértices:")
            problemas.extend(inconsistencias)

        if not self._eh_fortemente_conexo():
            problemas.append("❌ O grafo não é fortemente conexo.")

        return len(problemas) == 0, problemas


    def _eh_fortemente_conexo(self):
        """
        Verifica se o grafo é fortemente conexo, ou seja, se existe um caminho entre qualquer par de vértices em ambos os sentidos.

        Utiliza BFS no grafo e no grafo transposto.

        Retorna:
        bool: True se o grafo for fortemente conexo, False caso contrário.
        """
        if not self.vertices:
            return True

        def bfs(grafo, inicio):
            visitados = set()
            fila = deque([inicio])
            while fila:
                atual = fila.popleft()
                if atual not in visitados:
                    visitados.add(atual)
                    fila.extend(grafo.get(atual, {}))
            return visitados

        v0 = next(iter(self.vertices))
        normal = bfs(self.grafo, v0)

        reverso = defaultdict(dict)
        for u in self.grafo:
            for v in self.grafo[u]:
                reverso[v][u] = self.grafo[u][v]

        inverso = bfs(reverso, v0)

        return normal == self.vertices and inverso == self.vertices

    def vertices_ate_distancia(self, origem, distancia_max):
        """
        Retorna todos os vértices que estão a uma distância menor ou igual a D do vértice de origem,
        considerando a soma dos pesos das arestas (Dijkstra).

        Parâmetros:
        origem (str): E-mail de origem.
        distancia_max (int): Distância máxima permitida.

        Retorna:
        list[str]: Lista de e-mails alcançáveis dentro da distância D.
        """
        distancias = {origem: 0}
        fila = [(0, origem)]

        while fila:
            dist, atual = heapq.heappop(fila)

            # Importante: se já encontramos uma distância melhor, ignorar esta entrada
            if dist > distancias[atual]:
                continue

            for vizinho, peso in self.grafo.get(atual, {}).items():
                nova_dist = dist + peso
                if nova_dist <= distancia_max and (vizinho not in distancias or nova_dist < distancias[vizinho]):
                    distancias[vizinho] = nova_dist
                    heapq.heappush(fila, (nova_dist, vizinho))

        return [v for v in distancias if v != origem and distancias[v] <= distancia_max]


    def calcular_diametro(self):
        """
        Calcula o diâmetro do grafo, ou seja, o maior caminho mínimo entre todos os pares de vértices.

        Retorna:
        tuple[int, list[str]]: Comprimento do maior caminho mínimo e o caminho correspondente.
        """
        maior_caminho = 0
        caminho_mais_longo = []

        for origem in self.vertices:
            distancias, caminhos = self._dijkstra_com_caminhos(origem)
            for destino in distancias:
                if distancias[destino] > maior_caminho:
                    maior_caminho = distancias[destino]
                    caminho_mais_longo = caminhos[destino]

        return maior_caminho, caminho_mais_longo

    def _dijkstra_com_caminhos(self, origem):
        """
        Executa o algoritmo de Dijkstra para encontrar os menores caminhos a partir de um vértice de origem.

        Retorna:
        tuple[dict[str, int], dict[str, list[str]]]:
        - Dicionário com a menor distância até cada vértice.
        - Dicionário com o caminho seguido até cada vértice.
        """
        distancias = {origem: 0}
        caminhos = {origem: [origem]}
        fila = [(0, origem)]

        while fila:
            dist, atual = heapq.heappop(fila)
            for vizinho, peso in self.grafo.get(atual, {}).items():
                nova_dist = dist + peso
                if vizinho not in distancias or nova_dist < distancias[vizinho]:
                    distancias[vizinho] = nova_dist
                    caminhos[vizinho] = caminhos[atual] + [vizinho]
                    heapq.heappush(fila, (nova_dist, vizinho))

        return distancias, caminhos

# Exemplo de uso
if __name__ == "__main__":
    caminho_base = "./enron_emails"
    grafo = GrafoEnron()
    grafo.processar_emails(caminho_base)
    grafo.salvar_lista_adjacencias("lista_adjacencias.txt")
    print("Número de vértices:", grafo.numero_de_vertices())
    print("Número de arestas:", grafo.numero_de_arestas())
    print("Vértices isolados:", grafo.vertices_isolados())
    print("Top 20 saída:", grafo.top_20_grau_saida())
    print("Top 20 entrada:", grafo.top_20_grau_entrada())
    euleriano, motivos = grafo.grafo_euleriano()
    print("É Euleriano?", euleriano)
    if not euleriano:
        for m in motivos:
            print(" -", m)
    resultado = grafo.vertices_ate_distancia("gina.taylor@enron.com", 10)
    print("Vértices de gina.taylor@enron.com até distância 10:", resultado)
    diametro, caminho = grafo.calcular_diametro()
    print("Diâmetro do grafo:", diametro)
    print("Caminho mais longo:", caminho)
