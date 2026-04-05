import random
import heapq
import time
import os

# Códigos ANSI para colorir o terminal
AZUL    = "\033[94m"
VERMELHO = "\033[91m"
RESET   = "\033[0m"
CINZA   = "\033[90m"
AMARELO = "\033[93m"
VERDE   = "\033[92m"


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


class Labirinto:
    def __init__(self, n, num_paredes):
        self.n = n
        self.origem  = (0, 0)
        self.destino = (n - 1, n - 1)
        self.matriz  = self._gerar_matriz(num_paredes)

    def _gerar_matriz(self, num_paredes):
        """
        Monta o grid com grama (0, custo 1) e lama (5, custo 5) distribuídos
        aleatoriamente, depois insere as paredes (1) em posições livres.
        """
        matriz = [[random.choice([0, 5]) for _ in range(self.n)] for _ in range(self.n)]

        colocadas  = 0
        tentativas = 0
        limite     = self.n * self.n

        while colocadas < num_paredes and tentativas < limite:
            r = random.randint(0, self.n - 1)
            c = random.randint(0, self.n - 1)
            eh_ponto_fixo = (r, c) == self.origem or (r, c) == self.destino
            if not eh_ponto_fixo and matriz[r][c] != 1:
                matriz[r][c] = 1
                colocadas += 1
            tentativas += 1

        # Garante que início e fim sejam sempre acessíveis
        matriz[self.origem[0]][self.origem[1]]  = 0
        matriz[self.destino[0]][self.destino[1]] = 0
        return matriz

    def visualizar(self, caminho=None, visitados=None, titulo="Mapa"):
        """
        Imprime o labirinto no terminal com cores:
          - A / B em vermelho
          - caminho percorrido em azul
          - visitados (durante busca) em cinza
          - paredes, grama e lama com seus símbolos habituais
        """
        caminho_set  = set(caminho)  if caminho   else set()
        visitados_set = set(visitados) if visitados else set()

        print(f"\n--- {titulo} ---")

        for r in range(self.n):
            linha = ""
            for c in range(self.n):
                pos = (r, c)
                val = self.matriz[r][c]

                if pos == self.origem:
                    linha += f"{VERMELHO} A {RESET}"
                elif pos == self.destino:
                    linha += f"{VERMELHO} B {RESET}"
                elif pos in caminho_set:
                    linha += f"{AZUL} o {RESET}"
                elif pos in visitados_set:
                    linha += f"{CINZA} * {RESET}"
                elif val == 1:
                    linha += " | "
                elif val == 5:
                    linha += f"{AMARELO} ^ {RESET}"
                else:
                    linha += " _ "

            print(linha)

        print(
            f"Legenda: {VERMELHO}A/B{RESET} Início/Fim  "
            f"{AZUL}o{RESET} Caminho  "
            f"{CINZA}*{RESET} Visitado  "
            f"| Parede  "
            f"{AMARELO}^{RESET} Lama(5)  "
            f"_ Grama(1)"
        )

    def obter_vizinhos(self, pos):
        """Retorna as posições adjacentes que não sejam paredes."""
        r, c = pos
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        vizinhos = []
        for dr, dc in direcoes:
            nr, nc = r + dr, c + dc
            dentro_do_grid = 0 <= nr < self.n and 0 <= nc < self.n
            if dentro_do_grid and self.matriz[nr][nc] != 1:
                vizinhos.append((nr, nc))
        return vizinhos


# ---------------------------------------------------------------------------
# Animação separada da execução
# ---------------------------------------------------------------------------

def reproduzir_animacao(labirinto, historico_visitados, caminho, titulo, delay=0.05):
    """
    Recebe o histórico de nós visitados gravado durante a busca e
    reproduz frame a frame — completamente desacoplado do tempo medido.
    """
    visitados_ate_agora = []
    for no in historico_visitados:
        visitados_ate_agora.append(no)
        limpar_tela()
        labirinto.visualizar(visitados=visitados_ate_agora, titulo=f"{titulo} — explorando...")
        time.sleep(delay)

    # Frame final: mostra o caminho encontrado sobre os visitados
    limpar_tela()
    labirinto.visualizar(caminho=caminho, visitados=visitados_ate_agora, titulo=f"{titulo} — concluído!")


# ---------------------------------------------------------------------------
# Algoritmos de busca  (retornam também o histórico para a animação)
# ---------------------------------------------------------------------------

def busca_largura(labirinto):
    """
    BFS clássico — explora camada por camada (FIFO).
    Garante o menor número de passos, mas ignora o custo do terreno.
    O tempo é medido aqui dentro, sem nenhum sleep ou print.
    """
    inicio_t  = time.time()
    fronteira = [labirinto.origem]
    pais      = {labirinto.origem: None}
    historico = []   # ordem em que os nós foram expandidos

    while fronteira:
        no_atual = fronteira.pop(0)
        historico.append(no_atual)

        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(pais, no_atual), len(historico), tempo_ms, historico

        for vizinho in labirinto.obter_vizinhos(no_atual):
            if vizinho not in pais:
                pais[vizinho] = no_atual
                fronteira.append(vizinho)

    return None, len(historico), tempo_ms, historico


def busca_profundidade(labirinto):
    """
    DFS — mergulha fundo em um ramo antes de tentar outro (LIFO).
    Rápido em mapas simples, mas pode encontrar caminhos bem tortos.
    """
    inicio_t  = time.time()
    fronteira = [labirinto.origem]
    pais      = {labirinto.origem: None}
    historico = []

    while fronteira:
        no_atual = fronteira.pop()
        historico.append(no_atual)

        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(pais, no_atual), len(historico), tempo_ms, historico

        for vizinho in labirinto.obter_vizinhos(no_atual):
            if vizinho not in pais:
                pais[vizinho] = no_atual
                fronteira.append(vizinho)

    return None, len(historico), tempo_ms, historico


def busca_gulosa(labirinto):
    """
    Greedy Best-First — sempre avança em direção ao destino usando só a
    heurística de Manhattan. Ignora o custo real já acumulado.
    """
    inicio_t  = time.time()
    fronteira = []
    heapq.heappush(fronteira, (heuristica(labirinto.origem, labirinto.destino), labirinto.origem))
    pais      = {labirinto.origem: None}
    historico = []

    while fronteira:
        _, no_atual = heapq.heappop(fronteira)
        historico.append(no_atual)

        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(pais, no_atual), len(historico), tempo_ms, historico

        for vizinho in labirinto.obter_vizinhos(no_atual):
            if vizinho not in pais:
                pais[vizinho] = no_atual
                prioridade    = heuristica(vizinho, labirinto.destino)
                heapq.heappush(fronteira, (prioridade, vizinho))

    return None, len(historico), tempo_ms, historico


def busca_a_estrela(labirinto):
    """
    A* — combina custo real g(n) com estimativa h(n).
    É o único dos quatro que leva em conta tanto o peso do terreno
    quanto a distância até o destino, achando o caminho de menor custo.
    """
    inicio_t  = time.time()
    h_inicial = heuristica(labirinto.origem, labirinto.destino)
    fronteira = []
    heapq.heappush(fronteira, (h_inicial, labirinto.origem))

    pais      = {labirinto.origem: None}
    g_score   = {labirinto.origem: 0}
    historico = []

    while fronteira:
        _, no_atual = heapq.heappop(fronteira)
        historico.append(no_atual)

        if no_atual == labirinto.destino:
            tempo_ms = (time.time() - inicio_t) * 1000
            return reconstruir_caminho(pais, no_atual), len(historico), tempo_ms, historico

        for vizinho in labirinto.obter_vizinhos(no_atual):
            custo_terreno = 5 if labirinto.matriz[vizinho[0]][vizinho[1]] == 5 else 1
            novo_g        = g_score[no_atual] + custo_terreno

            if vizinho not in g_score or novo_g < g_score[vizinho]:
                g_score[vizinho] = novo_g
                pais[vizinho]    = no_atual
                f_score          = novo_g + heuristica(vizinho, labirinto.destino)
                heapq.heappush(fronteira, (f_score, vizinho))

    return None, len(historico), tempo_ms, historico


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def heuristica(a, b):
    """Distância de Manhattan entre dois pontos num grid de 4 direções."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruir_caminho(pais, atual):
    """Segue os ponteiros de pai em pai até chegar na origem e inverte a lista."""
    caminho = []
    while atual is not None:
        caminho.append(atual)
        atual = pais[atual]
    return caminho[::-1]


def calcular_custo(labirinto, caminho):
    if not caminho:
        return float("inf")
    return sum(5 if labirinto.matriz[r][c] == 5 else 1 for r, c in caminho)


def exibir_comparativo(resultados):
    if not resultados:
        print("\nNenhum algoritmo encontrou um caminho.")
        return

    print("\n" + "=" * 62)
    print(f"{'Algoritmo':<22} | {'Custo':^8} | {'Nós Exp.':^10} | {'Tempo (ms)':^10}")
    print("-" * 62)

    melhor_nome  = None
    menor_custo  = float("inf")

    for nome, info in resultados.items():
        print(
            f"{nome:<22} | {info['custo']:^8} | {info['expandidos']:^10} | {info['tempo']:^10.3f}"
        )
        if info["custo"] < menor_custo:
            menor_custo = info["custo"]
            melhor_nome = nome
        elif info["custo"] == menor_custo and melhor_nome:
            if info["expandidos"] < resultados[melhor_nome]["expandidos"]:
                melhor_nome = nome

    print("=" * 62)
    print(f"{VERDE}MELHOR ESTRATÉGIA: {melhor_nome}{RESET}")
    print("=" * 62)


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------

def main():
    limpar_tela()
    print("=== SISTEMA DE RESOLUÇÃO DE LABIRINTOS ===\n")

    try:
        n = int(input("Tamanho N do mapa (ex: 10): "))
        p = int(input("Quantidade de paredes:      "))
    except ValueError:
        print("Entrada inválida — use apenas números inteiros.")
        return

    lab = Labirinto(n, p)

    limpar_tela()
    lab.visualizar(titulo="LABIRINTO INICIAL")
    input("\nPressione Enter para iniciar as buscas...")

    estrategias = [
        ("Busca em Largura",     busca_largura),
        ("Busca em Profundidade", busca_profundidade),
        ("Busca Gulosa",          busca_gulosa),
        ("Busca A*",              busca_a_estrela),
    ]

    historico = {}

    for nome, algoritmo in estrategias:
        limpar_tela()
        print(f"Executando (sem animação): {nome}...")

        # 1) Roda o algoritmo puro — tempo medido aqui, sem sleep ou print
        caminho, expandidos, tempo, hist_visitados = algoritmo(lab)

        if caminho:
            custo = calcular_custo(lab, caminho)
            historico[nome] = {"custo": custo, "expandidos": expandidos, "tempo": tempo}

            # 2) Só depois de ter o tempo, reproduz a animação
            reproduzir_animacao(lab, hist_visitados, caminho, titulo=nome)
            print(f"\nCusto: {custo}  |  Nós expandidos: {expandidos}  |  Tempo real: {tempo:.4f} ms")
        else:
            limpar_tela()
            lab.visualizar(titulo=f"{nome} — sem saída")
            print(f"\n{nome}: não encontrou nenhum caminho possível.")

        input("\nPressione Enter para continuar...")

    limpar_tela()
    exibir_comparativo(historico)


if __name__ == "__main__":
    main()