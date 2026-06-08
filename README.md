# FLYFOOD - TSP com Forca Bruta e Algoritmo Genetico

Este projeto resolve uma adaptacao do Problema do Caixeiro Viajante para o FLYFOOD: um drone sai da base `R`, visita todos os pontos de entrega (`A`, `B`, `C`, ...) e retorna para `R`.

A distancia usada e Manhattan:

```text
distancia = |linha1 - linha2| + |coluna1 - coluna2|
```

Nos comandos abaixo, use `python main.py`. Se o Windows nao encontrar `python`, use o executavel Python disponivel no seu ambiente.

## Formato da entrada FLYFOOD

A primeira linha informa `linhas colunas`. Depois vem a matriz:

```text
4 4
R 0 A 0
0 0 0 0
B 0 0 C
0 0 0 0
```

Regras:

- `R`: base do drone.
- `0`: espaco vazio.
- Letras maiusculas: pontos de entrega.
- Deve existir exatamente uma base `R`.
- Deve existir pelo menos um ponto de entrega.

## Conversao para matriz triangular superior

O comando abaixo converte a instancia FLYFOOD para um arquivo no estilo TSPLIB usado por instancias como BRAIL58, com `EDGE_WEIGHT_TYPE: EXPLICIT` e `EDGE_WEIGHT_FORMAT: UPPER_ROW`.

```powershell
python main.py convert --input entrada.txt --output flyfood.tsp
```

Para o exemplo acima, a ordem dos nos e:

```text
R A B C
```

Coordenadas:

```text
R = (0, 0)
A = (0, 2)
B = (2, 0)
C = (2, 3)
```

Matriz completa de distancias Manhattan:

```text
0 2 2 5
2 0 4 3
2 4 0 3
5 3 3 0
```

Triangular superior sem diagonal (`UPPER_ROW`):

```text
2 2 5 4 3 3
```

## Resolver por forca bruta

```powershell
python main.py solve --method brute --input entrada.txt
```

A forca bruta testa todas as permutacoes possiveis, entao ela serve como validacao para instancias pequenas.

## Resolver por Algoritmo Genetico

Padrao: torneio binario para pais e esquema geracional para sobreviventes.

```powershell
python main.py solve --method ga --input entrada.txt --seed 42
```

Selecionar pais por torneio binario:

```powershell
python main.py solve --method ga --input entrada.txt --parent-selection tournament --tournament-size 2
```

Selecionar pais por roleta:

```powershell
python main.py solve --method ga --input entrada.txt --parent-selection roulette
```

Sobreviventes por esquema geracional:

```powershell
python main.py solve --method ga --input entrada.txt --survivor-selection generational
```

Sobreviventes por estado-estavel:

```powershell
python main.py solve --method ga --input entrada.txt --survivor-selection steady-state
```

Parametros uteis:

```powershell
python main.py solve --method ga --input entrada.txt --population-size 100 --generations 800 --mutation-rate 0.2 --seed 42
```

## Comparar AG versus Forca Bruta

```powershell
python main.py compare --input entrada.txt --runs 10 --seed 42
```

A comparacao imprime:

- melhor rota da forca bruta;
- melhor rota encontrada pelo AG;
- custo medio, melhor e pior custo do AG;
- tempo medio do AG;
- gap percentual do melhor AG em relacao a forca bruta.

Por seguranca, a comparacao bloqueia forca bruta acima de 10 entregas. Para aumentar o limite:

```powershell
python main.py compare --input entrada.txt --max-bruteforce-deliveries 11
```

## Execucao interativa

Sem argumentos, o programa mantem o uso antigo: pede a matriz pelo terminal e resolve por forca bruta.

```powershell
python main.py
```

## Integrantes

- Misael Marcos (BSI 25.2 UFRPE)
- Wanderson Mendonca (BSI 25.2 UFRPE)
- Artur Iarley (BSI 25.2 UFRPE)
- Luis Gabriel (BSI 25.2 UFRPE)
- Professor Cicero Garrozi (UFRPE)


