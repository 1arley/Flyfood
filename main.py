import itertools
import time

def distancia(p1, p2):
    """Calcula a distância de Manhattan entre dois pontos."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def validar_entrada(entrada):
    """Valida se a matriz informada segue as regras do problema."""
    try:
        linhas = entrada.strip().split('\n')

        # 1. primeira linha
        primeira = linhas[0].split()
        if len(primeira) != 2:
            return False, "A primeira linha deve conter dois números (linhas e colunas)."

        n, m = map(int, primeira)

        # 2. quantidade de linhas
        if len(linhas[1:]) != n:
            return False, f"Número de linhas incorreto. Esperado: {n}."

        origem_count = 0
        pontos = set()

        for linha in linhas[1:]:
            colunas = linha.split()

            # 3. verifica colunas
            if len(colunas) != m:
                return False, f"Número de colunas incorreto. Esperado: {m}."

            for celula in colunas:
                if celula == 'R':
                    origem_count += 1
                elif celula == '0':
                    continue
                elif celula.isalpha() and celula.isupper():
                    if celula in pontos:
                        return False, f"Ponto (item) repetido: {celula}"
                    pontos.add(celula)
                else:
                    return False, f"Valor inválido: {celula}"

        # 4. verifica
        if origem_count != 1:
            return False, "Deve haver exatamente um ponto de origem (R)."

        # 5. um ponto de entrega minimo
        if len(pontos) == 0:
            return False, "Deve haver pelo menos um item para entrega."

        return True, None

    except Exception as e:
        return False, f"Erro ao processar a entrada: {e}"


def resolver(entrada):
    """Encontra a melhor rota passando por todos os itens."""
    linhas = entrada.strip().split('\n')

    origem = None
    pontos = {}

    # Mapeia a localização da origem e dos itens
    for i, linha in enumerate(linhas[1:]):
        for j, celula in enumerate(linha.split()):
            if celula == 'R':
                origem = (i, j)
            elif celula != '0':
                pontos[celula] = (i, j)

    entregas = list(pontos.keys())

    menor_dist = float('inf')
    melhor_rota = None

    # Testa todas as permutações possíveis
    for rota in itertools.permutations(entregas):
        dist = 0
        atual = origem

        for ponto in rota:
            dist += distancia(atual, pontos[ponto])
            atual = pontos[ponto]

        # Retorna para a origem
        dist += distancia(atual, origem)

        if dist < menor_dist:
            menor_dist = dist
            melhor_rota = rota

    return " ".join(melhor_rota), menor_dist

while True:
    print("\nDigite a entrada da matriz (pressione ENTER duas vezes seguidas para finalizar e calcular):")
    
    linhas_input = []
    while True:
        linha = input()
        if linha == "":
            break
        linhas_input.append(linha)

    entrada = "\n".join(linhas_input)

    valido, erro = validar_entrada(entrada)

    if valido:
        break # Sai do loop se a entrada for válida
    else:
        print(f"\n❌ Entrada inválida: {erro}")
        print("Tente novamente.\n")

inicio_calculo = time.time()

rota, custo = resolver(entrada)

fim_calculo = time.time()
tempo_execucao = fim_calculo - inicio_calculo

print("\n" + "="*30)
print(f"✅ Rota: {rota}")
print(f"✅ Custo: {custo} dronômetros")
print(f"✅ Tempo de cálculo: {tempo_execucao:.6f} segundos")
print("="*30 + "\n")
