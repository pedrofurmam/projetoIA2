import random
import heapq
import time

class Labirinto:
    def __init__(self, n, num_paredes): 
        # n = tamanho do mapa, num_paredes = quantidade de paredes a serem colocadas definidas pelo usuário
        self.n = n
        self.origem = (0, 0)
        self.destino = (n - 1, n - 1)
        self.matriz = self._gerar_matriz_base(num_paredes)

    def _gerar_matriz_base(self, num_paredes):
        """
        Gera a matriz n x n. 
        0 = Grama (Custo 1)
        5 = Lama (Custo 5)
        1 = Parede (Intransponível)
        """
        matriz = [[random.choice([0, 5]) for _ in range(self.n)] for _ in range(self.n)]
        # Coloca os obstáculos 0 (grama) e 5 (lama) aleatoriamente, para definir a dificuldade do mapa.
        paredes_colocadas = 0
        tentativas = 0
        while paredes_colocadas < num_paredes and tentativas < (self.n * self.n): 
            r, c = random.randint(0, self.n - 1), random.randint(0, self.n - 1)
            if (r, c) != self.origem and (r, c) != self.destino and matriz[r][c] != 1:
                matriz[r][c] = 1 # Coloca uma parede
                paredes_colocadas += 1 # Conta até que se alcance o número inserido de paredes
            tentativas += 1
        
        # Garante que os pontos A e B sejam "passáveis"
        matriz[self.origem[0]][self.origem[1]] = 0
        matriz[self.destino[0]][self.destino[1]] = 0
        return matriz

    def visualizar(self, caminho=None, titulo="Mapa"): 
        # Visualiza o labirinto no console, destacando o caminho encontrado (se houver) e os obstáculos.
        caminho_set = set(caminho) if caminho else set()
        print(f"\n--- {titulo} ---")
        for r in range(self.n):
            linha = ""
            for c in range(self.n):
                pos = (r, c)
                val = self.matriz[r][c]
                if pos == self.origem: linha += " A "
                elif pos == self.destino: linha += " B "
                elif pos in caminho_set: linha += " o "
                elif val == 1: linha += " | "
                elif val == 5: linha += " ^ "
                else: linha += " _ "
            print(linha)
        print("Legenda: A (Início), B (Fim), | (Parede), ^ (Lama/Custo 5), _ (Grama/Custo 1), o (Caminho)")

    def obter_sucessores(self, pos):
        # Posicionamento atual e retorna os sucessores válidos
        r, c = pos
        sucessores = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.n and self.matriz[nr][nc] != 1:
                sucessores.append((nr, nc))
        return sucessores

# --- Algoritmos de Busca ---

def busca_largura(labirinto):
    # Visualiza todos os caminhos possíveis simultaneamente
    inicio_t = time.time()
    fronteira = [labirinto.origem] 
    visitados = {labirinto.origem: None}
    nos_expandidos = 0

    while fronteira:
        # FIFO: pop(0) para remover o primeiro elemento da lista
        no_atual = fronteira.pop(0) 
        nos_expandidos += 1

        # Teste de objetivo
        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(visitados, no_atual), nos_expandidos, tempo_ms

        # Expansão
        for sucessor in labirinto.obter_sucessores(no_atual):
            if sucessor not in visitados:
                visitados[sucessor] = no_atual
                fronteira.append(sucessor)
    
    return None, nos_expandidos, 0

def busca_profundidade(labirinto):
    # Escolhe um caminho e segue "reto toda vida" até chegar a um beco sem saída, então volta e tenta de novo
    inicio_t = time.time()
    fronteira = [labirinto.origem] # LIFO para DFS
    visitados = {labirinto.origem: None}
    nos_expandidos = 0

    while fronteira:
        no_atual = fronteira.pop()
        nos_expandidos += 1

        # Teste de objetivo
        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(visitados, no_atual), nos_expandidos, tempo_ms

        # Expansão
        for sucessor in labirinto.obter_sucessores(no_atual):
            if sucessor not in visitados:
                visitados[sucessor] = no_atual
                fronteira.append(sucessor)
                
    return None, nos_expandidos, 0

def busca_gulosa(labirinto):
    inicio_t = time.time()
    # A fila de prioridade armazena: (valor_da_heuristica, no_atual)
    # A Gulosa expande sempre o nó com a menor HEURÍSTICA.
    # Ela ignora o custo do terreno (lama/grama) já percorrido.
    # O heapq sempre retira o que tiver o menor valor de prioridade primeiro
    fronteira = []
    heapq.heappush(fronteira, (heuristica(labirinto.origem, labirinto.destino), labirinto.origem))
    
    visitados = {labirinto.origem: None}
    nos_expandidos = 0

    while fronteira:
        # O '_' ignora o valor da heurística, pegamos apenas a posição do nó
        _, no_atual = heapq.heappop(fronteira)
        nos_expandidos += 1

        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(visitados, no_atual), nos_expandidos, tempo_ms

        for sucessor in labirinto.obter_sucessores(no_atual):
            if sucessor not in visitados:
                visitados[sucessor] = no_atual
                prioridade = heuristica(sucessor, labirinto.destino)
                heapq.heappush(fronteira, (prioridade, sucessor))
                
    return None, nos_expandidos, 0

def busca_a_estrela(labirinto):
    inicio_t = time.time()
    # A fila de prioridade armazena: (f_score, no_atual)
    # f(n) = g(n) + h(n)
    # g(n): Custo real acumulado do ponto de partida até aqui.
    # h(n): Estimativa (heurística) daqui até o objetivo.
    fronteira = []
    # No início, g é 0, então f = h
    h_inicial = heuristica(labirinto.origem, labirinto.destino)
    heapq.heappush(fronteira, (h_inicial, labirinto.origem))
    
    visitados = {labirinto.origem: None}
    # g_score armazena o custo real acumulado para chegar em cada nó
    g_score = {labirinto.origem: 0}
    nos_expandidos = 0

    while fronteira:
        _, no_atual = heapq.heappop(fronteira)
        nos_expandidos += 1

        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(visitados, no_atual), nos_expandidos, tempo_ms

        for sucessor in labirinto.obter_sucessores(no_atual):
            # Calcula o custo real somando o peso do terreno definido no mapa.
            #Foi definido: 5 para lama, senão 1 (grama)
            custo_terreno = 5 if labirinto.matriz[sucessor[0]][sucessor[1]] == 5 else 1
            novo_g = g_score[no_atual] + custo_terreno
            
            # O A* só atualiza o caminho se encontrar uma rota MAIS BARATA (menor g).
            if sucessor not in g_score or novo_g < g_score[sucessor]:
                g_score[sucessor] = novo_g
                visitados[sucessor] = no_atual
                f_score = novo_g + heuristica(sucessor, labirinto.destino)
                heapq.heappush(fronteira, (f_score, sucessor))
                
    return None, nos_expandidos, 0


# --- Utilitários de Análise ---

def heuristica(a, b):
    # Calcula a distância de Manhattan entre o ponto 'a' e o ponto 'b'
    # é permitido apenas em 4 direções (cima, baixo, esquerda, direita).
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruir_caminho(parentes, atual):
    # Volta e tenta de novo da busca_profundidade 
    caminho = []
    while atual is not None:
        caminho.append(atual)
        atual = parentes[atual]
    return caminho[::-1]

def calcular_custo(labirinto, caminho):
    # Verifica cada posição encontrada e soma o custo conforme os obstáculos ou caminho livre
    if not caminho: return float('inf')
    # Custo 1 para grama (0) e custo 5 para lama (5)
    return sum(5 if labirinto.matriz[r][c] == 5 else 1 for r, c in caminho)

def exibir_melhor_caminho(resultados):
    # Compara e exibe o melhor 
    if not resultados:
        print("\nNenhum caminho foi encontrado por nenhum algoritmo.")
        return

    print("\n" + "="*60)
    print(f"{'Algoritmo':<20} | {'Custo':<10} | {'Nós Exp.':<10} | {'Tempo (ms)':<10}")
    print("-" * 60)
    
    melhor_nome = None
    menor_custo = float('inf')

    for nome, info in resultados.items():
        print(f"{nome:<20} | {info['custo']:<10} | {info['expandidos']:<10} | {info['tempo']:<10.4f}")
        
        # Critério: Menor custo total, desempate por menor número de nós expandidos
        if info['custo'] < menor_custo:
            menor_custo = info['custo']
            melhor_nome = nome
        elif info['custo'] == menor_custo:
            if melhor_nome and info['expandidos'] < resultados[melhor_nome]['expandidos']:
                melhor_nome = nome

    print("="*60)
    print(f"MELHOR ESTRATÉGIA: {melhor_nome}")
    print("="*60)

# --- Execução Principal ---

def main():
    print("=== SISTEMA DE RESOLUÇÃO DE LABIRINTOS ===")
    try:
        n = int(input("Informe o tamanho N do mapa: "))
        p = int(input("Informe a quantidade de paredes: "))
    except ValueError:
        print("Entrada inválida. Use apenas números inteiros.")
        return

    lab = Labirinto(n, p)
    lab.visualizar(titulo="LABIRINTO INICIAL")

    historico_resultados = {}

    estrategias = [
        ("Busca em Largura", busca_largura),
        ("Busca em Profundidade", busca_profundidade),
        ("Busca Gulosa", busca_gulosa),
        ("Busca A*", busca_a_estrela)
    ]

    for nome, algoritmo in estrategias:
        print(f"\nCalculando {nome}...")
        caminho, expandidos, tempo = algoritmo(lab)
        
        if caminho:
            custo = calcular_custo(lab, caminho)
            historico_resultados[nome] = {
                'custo': custo,
                'expandidos': expandidos,
                'tempo': tempo
            }
            lab.visualizar(caminho, titulo=f"RESULTADO: {nome}")
            print(f"Custo Total: {custo} | Nós Expandidos: {expandidos} | Tempo: {tempo:.4f} ms")
        else:
            print(f"O algoritmo {nome} não encontrou saída.")

    exibir_melhor_caminho(historico_resultados)

if __name__ == "__main__":
    main()
    #print(heuristica((0,0), (3,3)))