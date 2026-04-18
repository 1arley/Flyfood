import itertools


# Distância de Manhattan — sem diagonal, só horizontal/vertical
def distancia(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def resolver(entrada):
    linhas = entrada.strip().split('\n')

    origem = None
    pontos = {}

    # Percorre a matriz pulando a primeira linha (que tem as dimensões)
    for i, linha in enumerate(linhas[1:]):
        for j, celula in enumerate(linha.split()):
            if celula == 'R':
                origem = (i, j)
            elif celula != '0':
                pontos[celula] = (i, j)

    entregas = list(pontos.keys())

    menor_dist = float('inf')
    melhor_rota = None

    # Testa todas as ordens possíveis de entrega (força bruta mesmo)
    for rota in itertools.permutations(entregas):
        dist = 0
        atual = origem

        for ponto in rota:
            dist += distancia(atual, pontos[ponto])
            atual = pontos[ponto]

        # Não esquece de voltar pro ponto R no final
        dist += distancia(atual, origem)

        if dist < menor_dist:
            menor_dist = dist
            melhor_rota = rota

    return " ".join(melhor_rota), menor_dist


# --- teste com o exemplo do enunciado ---

entrada = """4 5
0 0 0 0 D
0 A 0 0 0
0 0 0 0 C
R 0 B 0 0"""

rota, custo = resolver(entrada)
print(f"Rota: {rota}")
print(f"Custo: {custo} dronômetros")