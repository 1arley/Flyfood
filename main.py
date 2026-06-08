import argparse
import itertools
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ORIGIN_LABEL = "R"


@dataclass(frozen=True)
class FlyfoodInstance:
    rows: int
    columns: int
    origin: tuple[int, int]
    deliveries: dict[str, tuple[int, int]]

    @property
    def delivery_labels(self) -> list[str]:
        return sorted(self.deliveries)

    @property
    def node_labels(self) -> list[str]:
        return [ORIGIN_LABEL, *self.delivery_labels]

    @property
    def coordinates(self) -> dict[str, tuple[int, int]]:
        return {ORIGIN_LABEL: self.origin, **self.deliveries}


@dataclass(frozen=True)
class RouteResult:
    route: tuple[str, ...]
    cost: int
    elapsed_seconds: float


@dataclass(frozen=True)
class GAConfig:
    population_size: int = 80
    generations: int = 400
    parent_selection: str = "tournament"
    survivor_selection: str = "generational"
    crossover_rate: float = 0.9
    mutation_rate: float = 0.15
    tournament_size: int = 2
    elite_size: int = 1
    seed: int | None = None


def manhattan_distance(point_a: tuple[int, int], point_b: tuple[int, int]) -> int:
    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])


def parse_flyfood_grid(text: str) -> FlyfoodInstance:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        raise ValueError("A entrada esta vazia.")

    dimensions = lines[0].split()
    if len(dimensions) != 2:
        raise ValueError("A primeira linha deve conter dois numeros: linhas e colunas.")

    rows, columns = map(int, dimensions)
    grid_lines = lines[1:]
    if len(grid_lines) != rows:
        raise ValueError(f"Numero de linhas incorreto. Esperado: {rows}.")

    origin = None
    deliveries: dict[str, tuple[int, int]] = {}

    for row_index, line in enumerate(grid_lines):
        cells = line.split()
        if len(cells) != columns:
            raise ValueError(f"Numero de colunas incorreto na linha {row_index + 1}. Esperado: {columns}.")

        for column_index, cell in enumerate(cells):
            if cell == "0":
                continue
            if cell == ORIGIN_LABEL:
                if origin is not None:
                    raise ValueError("Deve haver exatamente uma origem R.")
                origin = (row_index, column_index)
                continue
            if cell.isalpha() and cell.isupper() and len(cell) == 1:
                if cell in deliveries:
                    raise ValueError(f"Ponto de entrega repetido: {cell}.")
                deliveries[cell] = (row_index, column_index)
                continue
            raise ValueError(f"Valor invalido na matriz: {cell}.")

    if origin is None:
        raise ValueError("Deve haver exatamente uma origem R.")
    if not deliveries:
        raise ValueError("Deve haver pelo menos um ponto de entrega.")

    return FlyfoodInstance(rows=rows, columns=columns, origin=origin, deliveries=deliveries)


def build_distance_matrix(instance: FlyfoodInstance) -> list[list[int]]:
    labels = instance.node_labels
    coordinates = instance.coordinates
    return [
        [manhattan_distance(coordinates[row_label], coordinates[column_label]) for column_label in labels]
        for row_label in labels
    ]


def upper_row_values(matrix: list[list[int]]) -> list[int]:
    return [
        matrix[row][column]
        for row in range(len(matrix))
        for column in range(row + 1, len(matrix))
    ]


def format_tsplib_upper_row(instance: FlyfoodInstance, name: str = "FLYFOOD") -> str:
    labels = instance.node_labels
    matrix = build_distance_matrix(instance)
    values = upper_row_values(matrix)
    chunks = [" ".join(map(str, values[index:index + 12])) for index in range(0, len(values), 12)]

    return "\n".join(
        [
            f"NAME: {name}",
            "COMMENT: Distancias Manhattan convertidas da matriz FLYFOOD.",
            f"COMMENT: Ordem dos nos: {' '.join(labels)}",
            "TYPE: TSP",
            f"DIMENSION: {len(labels)}",
            "EDGE_WEIGHT_TYPE: EXPLICIT",
            "EDGE_WEIGHT_FORMAT: UPPER_ROW",
            "EDGE_WEIGHT_SECTION",
            *chunks,
            "EOF",
        ]
    )


def route_cost(route: tuple[str, ...] | list[str], instance: FlyfoodInstance) -> int:
    coordinates = instance.coordinates
    current_label = ORIGIN_LABEL
    total = 0

    for next_label in route:
        total += manhattan_distance(coordinates[current_label], coordinates[next_label])
        current_label = next_label

    total += manhattan_distance(coordinates[current_label], coordinates[ORIGIN_LABEL])
    return total


def solve_brute_force(instance: FlyfoodInstance) -> RouteResult:
    started_at = time.perf_counter()
    best_route: tuple[str, ...] | None = None
    best_cost = sys.maxsize

    for candidate in itertools.permutations(instance.delivery_labels):
        candidate_cost = route_cost(candidate, instance)
        if candidate_cost < best_cost:
            best_cost = candidate_cost
            best_route = candidate

    elapsed = time.perf_counter() - started_at
    if best_route is None:
        raise ValueError("Nao foi possivel gerar uma rota.")

    return RouteResult(route=best_route, cost=best_cost, elapsed_seconds=elapsed)


def make_initial_population(labels: list[str], population_size: int, rng: random.Random) -> list[tuple[str, ...]]:
    population = [tuple(labels)]
    seen = {population[0]}

    while len(population) < population_size:
        candidate = labels[:]
        rng.shuffle(candidate)
        candidate_tuple = tuple(candidate)
        if candidate_tuple in seen and len(seen) < factorial_limit(labels):
            continue
        population.append(candidate_tuple)
        seen.add(candidate_tuple)

    return population


def factorial_limit(labels: list[str]) -> int:
    value = 1
    for number in range(2, len(labels) + 1):
        value *= number
    return value


def select_parent(
    population: list[tuple[str, ...]],
    costs: dict[tuple[str, ...], int],
    config: GAConfig,
    rng: random.Random,
) -> tuple[str, ...]:
    if config.parent_selection == "tournament":
        competitors = rng.sample(population, k=min(config.tournament_size, len(population)))
        return min(competitors, key=lambda route: costs[route])

    if config.parent_selection == "roulette":
        best_cost = min(costs[route] for route in population)
        if best_cost == 0:
            return min(population, key=lambda route: costs[route])
        weights = [1 / costs[route] for route in population]
        return rng.choices(population, weights=weights, k=1)[0]

    raise ValueError(f"Selecao de pais desconhecida: {config.parent_selection}.")


def ordered_crossover(parent_a: tuple[str, ...], parent_b: tuple[str, ...], rng: random.Random) -> tuple[str, ...]:
    if len(parent_a) < 2:
        return parent_a

    start, end = sorted(rng.sample(range(len(parent_a)), k=2))
    child: list[str | None] = [None] * len(parent_a)
    child[start:end + 1] = parent_a[start:end + 1]

    insertion_index = (end + 1) % len(parent_a)
    for gene in parent_b[end + 1:] + parent_b[:end + 1]:
        if gene in child:
            continue
        child[insertion_index] = gene
        insertion_index = (insertion_index + 1) % len(parent_a)

    return tuple(gene for gene in child if gene is not None)


def mutate(route: tuple[str, ...], mutation_rate: float, rng: random.Random) -> tuple[str, ...]:
    if len(route) < 2 or rng.random() >= mutation_rate:
        return route

    mutated = list(route)
    first, second = rng.sample(range(len(mutated)), k=2)
    mutated[first], mutated[second] = mutated[second], mutated[first]
    return tuple(mutated)


def create_offspring(
    population: list[tuple[str, ...]],
    costs: dict[tuple[str, ...], int],
    config: GAConfig,
    rng: random.Random,
) -> list[tuple[str, ...]]:
    offspring: list[tuple[str, ...]] = []

    while len(offspring) < len(population):
        parent_a = select_parent(population, costs, config, rng)
        parent_b = select_parent(population, costs, config, rng)

        if rng.random() < config.crossover_rate:
            child_a = ordered_crossover(parent_a, parent_b, rng)
            child_b = ordered_crossover(parent_b, parent_a, rng)
        else:
            child_a, child_b = parent_a, parent_b

        offspring.append(mutate(child_a, config.mutation_rate, rng))
        if len(offspring) < len(population):
            offspring.append(mutate(child_b, config.mutation_rate, rng))

    return offspring


def solve_genetic_algorithm(instance: FlyfoodInstance, config: GAConfig) -> RouteResult:
    validate_ga_config(config)
    labels = instance.delivery_labels
    if len(labels) <= 2:
        return solve_brute_force(instance)

    rng = random.Random(config.seed)
    started_at = time.perf_counter()
    population = make_initial_population(labels, max(2, config.population_size), rng)

    def evaluate(routes: list[tuple[str, ...]]) -> dict[tuple[str, ...], int]:
        return {route: route_cost(route, instance) for route in routes}

    costs = evaluate(population)

    for _ in range(config.generations):
        offspring = create_offspring(population, costs, config, rng)
        offspring_costs = evaluate(offspring)

        if config.survivor_selection == "generational":
            elite_count = min(config.elite_size, len(population))
            elite = sorted(population, key=lambda route: costs[route])[:elite_count]
            population = elite + sorted(offspring, key=lambda route: offspring_costs[route])[:len(population) - elite_count]
        elif config.survivor_selection == "steady-state":
            combined = population + offspring
            combined_costs = {**costs, **offspring_costs}
            population = sorted(combined, key=lambda route: combined_costs[route])[:len(population)]
        else:
            raise ValueError(f"Selecao de sobreviventes desconhecida: {config.survivor_selection}.")

        costs = evaluate(population)

    best_route = min(population, key=lambda route: costs[route])
    elapsed = time.perf_counter() - started_at
    return RouteResult(route=best_route, cost=costs[best_route], elapsed_seconds=elapsed)


def compare_algorithms(instance: FlyfoodInstance, config: GAConfig, runs: int, max_bruteforce_deliveries: int) -> str:
    if runs < 1:
        raise ValueError("O numero de execucoes do AG deve ser pelo menos 1.")
    if len(instance.delivery_labels) > max_bruteforce_deliveries:
        raise ValueError(
            "Forca bruta bloqueada por seguranca: "
            f"{len(instance.delivery_labels)} entregas excedem o limite {max_bruteforce_deliveries}."
        )

    brute = solve_brute_force(instance)
    ga_results = [
        solve_genetic_algorithm(instance, GAConfig(**{**config.__dict__, "seed": None if config.seed is None else config.seed + run}))
        for run in range(runs)
    ]

    best_ga = min(ga_results, key=lambda result: result.cost)
    costs = [result.cost for result in ga_results]
    times = [result.elapsed_seconds for result in ga_results]
    gap = ((best_ga.cost - brute.cost) / brute.cost) * 100

    return "\n".join(
        [
            "Comparacao FLYFOOD",
            f"Nos: {len(instance.node_labels)} | Entregas: {len(instance.delivery_labels)}",
            f"Forca bruta: rota {' '.join(brute.route)} | custo {brute.cost} | tempo {brute.elapsed_seconds:.6f}s",
            f"AG melhor: rota {' '.join(best_ga.route)} | custo {best_ga.cost} | tempo {best_ga.elapsed_seconds:.6f}s",
            f"AG media de custo: {statistics.mean(costs):.2f} | melhor {min(costs)} | pior {max(costs)}",
            f"AG tempo medio: {statistics.mean(times):.6f}s em {runs} execucao(oes)",
            f"Gap do melhor AG vs forca bruta: {gap:.2f}%",
        ]
    )


def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        return read_interactive_input()
    return sys.stdin.read()


def validate_ga_config(config: GAConfig) -> None:
    if config.population_size < 2:
        raise ValueError("O tamanho da populacao deve ser pelo menos 2.")
    if config.generations < 0:
        raise ValueError("O numero de geracoes nao pode ser negativo.")
    if not 0 <= config.crossover_rate <= 1:
        raise ValueError("A taxa de crossover deve estar entre 0 e 1.")
    if not 0 <= config.mutation_rate <= 1:
        raise ValueError("A taxa de mutacao deve estar entre 0 e 1.")
    if config.tournament_size < 1:
        raise ValueError("O tamanho do torneio deve ser pelo menos 1.")
    if config.elite_size < 0:
        raise ValueError("O tamanho da elite nao pode ser negativo.")


def read_interactive_input() -> str:
    print("Digite a matriz FLYFOOD. Pressione ENTER duas vezes para finalizar:")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def write_output(path: str | None, text: str) -> None:
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
        print(f"Arquivo gerado: {path}")
        return
    print(text)


def print_route_result(label: str, result: RouteResult) -> None:
    print(f"{label}:")
    print(f"Rota: {' '.join(result.route)}")
    print(f"Custo: {result.cost} dronometros")
    print(f"Tempo: {result.elapsed_seconds:.6f}s")


def build_ga_config(args: argparse.Namespace) -> GAConfig:
    return GAConfig(
        population_size=args.population_size,
        generations=args.generations,
        parent_selection=args.parent_selection,
        survivor_selection=args.survivor_selection,
        crossover_rate=args.crossover_rate,
        mutation_rate=args.mutation_rate,
        tournament_size=args.tournament_size,
        elite_size=args.elite_size,
        seed=args.seed,
    )


def add_ga_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--population-size", type=int, default=80)
    parser.add_argument("--generations", type=int, default=400)
    parser.add_argument("--parent-selection", choices=["tournament", "roulette"], default="tournament")
    parser.add_argument("--survivor-selection", choices=["generational", "steady-state"], default="generational")
    parser.add_argument("--crossover-rate", type=float, default=0.9)
    parser.add_argument("--mutation-rate", type=float, default=0.15)
    parser.add_argument("--tournament-size", type=int, default=2)
    parser.add_argument("--elite-size", type=int, default=1)
    parser.add_argument("--seed", type=int, default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FLYFOOD: conversao, forca bruta e algoritmo genetico.")
    subparsers = parser.add_subparsers(dest="command")

    convert_parser = subparsers.add_parser("convert", help="Converte a matriz FLYFOOD para TSPLIB UPPER_ROW.")
    convert_parser.add_argument("--input", "-i")
    convert_parser.add_argument("--output", "-o")
    convert_parser.add_argument("--name", default="FLYFOOD")

    solve_parser = subparsers.add_parser("solve", help="Resolve a instancia por forca bruta ou AG.")
    solve_parser.add_argument("--input", "-i")
    solve_parser.add_argument("--method", choices=["brute", "ga"], default="brute")
    add_ga_arguments(solve_parser)

    compare_parser = subparsers.add_parser("compare", help="Compara AG com forca bruta.")
    compare_parser.add_argument("--input", "-i")
    compare_parser.add_argument("--runs", type=int, default=5)
    compare_parser.add_argument("--max-bruteforce-deliveries", type=int, default=10)
    add_ga_arguments(compare_parser)

    return parser


def run_command(args: argparse.Namespace) -> None:
    if args.command is None:
        instance = parse_flyfood_grid(read_interactive_input())
        print_route_result("Forca bruta", solve_brute_force(instance))
        return

    instance = parse_flyfood_grid(read_input(args.input))

    if args.command == "convert":
        write_output(args.output, format_tsplib_upper_row(instance, args.name))
        return

    if args.command == "solve":
        if args.method == "brute":
            print_route_result("Forca bruta", solve_brute_force(instance))
            return
        print_route_result("Algoritmo genetico", solve_genetic_algorithm(instance, build_ga_config(args)))
        return

    if args.command == "compare":
        print(compare_algorithms(instance, build_ga_config(args), args.runs, args.max_bruteforce_deliveries))


def main() -> None:
    parser = build_parser()
    try:
        run_command(parser.parse_args())
    except ValueError as error:
        print(f"Erro: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
