import itertools


def distancia(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def validar_entrada(entrada):
    try:
        linhas = entrada.strip().split('\n')

        # 1. primeira linha
        primeira = linhas[0].split()
        if len(primeira) != 2:
            return False, "A primeira linha deve conter dois números."

        n, m = map(int, primeira)

        # 2. quantidade de linhas
        if len(linhas[1:]) != n:
            return False, "Número de linhas incorreto."

        origem_count = 0
        pontos = set()

        for linha in linhas[1:]:
            colunas = linha.split()

            # 3. verifica colunas
            if len(colunas) != m:
                return False, "Número de colunas incorreto."

            for celula in colunas:
                if celula == 'R':
                    origem_count += 1
                elif celula == '0':
                    continue
                elif celula.isalpha() and celula.isupper():
                    if celula in pontos:
                        return False, f"Ponto repetido: {celula}"
                    pontos.add(celula)
                else:
                    return False, f"Valor inválido: {celula}"

        # 4. verifica
        if origem_count != 1:
            return False, "Deve haver exatamente um ponto de origem (R)."

        # 5. um ponto de entrega minimo
        if len(pontos) == 0:
            return False, "Deve haver pelo menos um ponto de entrega."

        return True, None

    except:
        return False, "Erro ao processar a entrada."


def resolver(entrada):
    linhas = entrada.strip().split('\n')

    origem = None
    pontos = {}

    for i, linha in enumerate(linhas[1:]):
        for j, celula in enumerate(linha.split()):
            if celula == 'R':
                origem = (i, j)
            elif celula != '0':
                pontos[celula] = (i, j)

    entregas = list(pontos.keys())

    menor_dist = float('inf')
    melhor_rota = None

    for rota in itertools.permutations(entregas):
        dist = 0
        atual = origem

        for ponto in rota:
            dist += distancia(atual, pontos[ponto])
            atual = pontos[ponto]

        dist += distancia(atual, origem)

        if dist < menor_dist:
            menor_dist = dist
            melhor_rota = rota

    return " ".join(melhor_rota), menor_dist


# loop de entrada
while True:
    print("\nDigite a entrada (pressione ENTER duas vezes para finalizar):")
    
    linhas_input = []
    while True:
        linha = input()
        if linha == "":
            break
        linhas_input.append(linha)

    entrada = "\n".join(linhas_input)

    valido, erro = validar_entrada(entrada)

    if valido:
        break
    else:
        print(f"\n❌ Entrada inválida: {erro}")
        print("Tente novamente.\n")


# final
rota, custo = resolver(entrada)
print(f"\n✅ Rota: {rota}")
print(f"✅ Custo: {custo} dronômetros")
