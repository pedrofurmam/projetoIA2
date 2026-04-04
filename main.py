import random
import time
from collections import deque

class Labirinto:
    def __init__(self, n, num_paredes):
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
        
        paredes_colocadas = 0
        tentativas = 0
        while paredes_colocadas < num_paredes and tentativas < (self.n * self.n):
            r, c = random.randint(0, self.n - 1), random.randint(0, self.n - 1)
            if (r, c) != self.origem and (r, c) != self.destino and matriz[r][c] != 1:
                matriz[r][c] = 1
                paredes_colocadas += 1
            tentativas += 1
        
        # Garante que os pontos A e B sejam passáveis
        matriz[self.origem[0]][self.origem[1]] = 0
        matriz[self.destino[0]][self.destino[1]] = 0
        return matriz

    def visualizar(self, caminho=None, titulo="Mapa"):
        """ Traduz a matriz numérica para caracteres visuais """
        caminho_set = set(caminho) if caminho else set()
        print(f"\n--- {titulo} ---")
        for r in range(self.n):
            linha = ""
            for c in range(self.n):
                pos = (r, c)
                val = self.matriz[r][c]
                if pos == self.origem: linha += " A "
                elif pos == self.destino: linha += " B "
                elif pos in caminho_set: linha += " . "
                elif val == 1: linha += " | "
                elif val == 5: linha += " ~ "
                else: linha += " _ "
            print(linha)
        print("Legenda: A (Início), B (Fim), | (Parede), ~ (Lama/Custo 5), _ (Grama/Custo 1), . (Caminho)")

    def obter_sucessores(self, pos):
        r, c = pos
        sucessores = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.n and self.matriz[nr][nc] != 1:
                sucessores.append((nr, nc))
        return sucessores

# --- Algoritmos de Busca ---

def busca_largura(labirinto):
    inicio_t = time.time()
    fronteira = deque([labirinto.origem]) # FIFO para BFS
    visitados = {labirinto.origem: None}
    nos_expandidos = 0

    while fronteira:
        no_atual = fronteira.popleft()
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

# --- Utilitários de Análise ---

def reconstruir_caminho(parentes, atual):
    caminho = []
    while atual is not None:
        caminho.append(atual)
        atual = parentes[atual]
    return caminho[::-1]

def calcular_custo(labirinto, caminho):
    if not caminho: return float('inf')
    # Custo 1 para grama (0) e custo 5 para lama (5)
    return sum(5 if labirinto.matriz[r][c] == 5 else 1 for r, c in caminho)

def exibir_melhor_caminho(resultados):
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
        ("Busca em Profundidade", busca_profundidade)
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