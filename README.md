# 🚁 FLYFOOD (Caixeiro Viajante)

Este projeto resolve uma adaptação do clássico **Problema do Caixeiro Viajante (TSP - *Traveling Salesperson Problem*)** aplicado a um drone de entregas. 

O script calcula a rota mais curta para um drone sair de sua base, entregar pacotes em diferentes pontos de uma cidade (representada por uma matriz/grade) e retornar à base, gastando a menor bateria (distância) possível.

## 📌 Sobre o Projeto

O mapa do problema é representado por uma grade 2D, simulando quarteirões de uma cidade. Por conta disso, o drone não pode voar nas diagonais. Para calcular o deslocamento, o algoritmo utiliza a **Distância de Manhattan** (apenas movimentos horizontais e verticais).

### Regras do Mapa:
- `R`: Representa a base do drone (ponto de partida e chegada).
- `0`: Representa espaços vazios no mapa.
- `Letras (A, B, C...)`: Representam os pontos de entrega.
- A primeira linha da entrada indica as dimensões da matriz (Linhas x Colunas).

## 🧠 Como Funciona o Algoritmo

1. **Mapeamento:** O código varre a matriz (ignorando os `0`s) e salva as coordenadas `(linha, coluna)` da base e de cada ponto de entrega.
2. **Força Bruta (Permutação):** Utilizando a biblioteca nativa `itertools`, o script gera **todas as combinações possíveis** de rotas de entrega.
3. **Cálculo de Custo:** Para cada rota, ele calcula a distância da base até a primeira entrega, entre as entregas seguintes, e a volta para a base.
4. **Otimização:** A rota que acumular a menor distância total ("dronômetros") é eleita a vencedora.

⚠️ *Nota de Desempenho:* Por usar força bruta (complexidade fatorial $O(N!)$), este script é ideal para mapas com um número pequeno de entregas. Para muitos pontos, seriam necessárias abordagens heurísticas (como Algoritmos Genéticos ou Vizinho Mais Próximo).

## 🚀 Como Executar

O projeto foi escrito em **Python** e não requer a instalação de bibliotecas externas (dependências).

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
