from typing import Union
from enum import Enum
from datetime import datetime
import networkx as nx
import numpy as np
import itertools
import ctypes.util
import ctypes
import typer
import random
import time
import csv
import sys

PINT = ctypes.POINTER(ctypes.c_int)
INF = np.iinfo(np.intc).max//2 - 1


class Algorithm(Enum):
    SEQUENTIAL_FLOYD_WARSHALL = 1
    PARALLEL_FLOYD_WARSHALL = 2


def random_u8_sequence(n: int):
    while n > 0:
        yield random.randint(0, 255)
        n -= 1

def generate_graph(n: int, m: int, seed: int) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_nodes_from(range(n))

    possible_edges = list(itertools.permutations(range(n), 2))
    random.seed(seed)
    edges = random.sample(possible_edges, k=m)
    ws = random_u8_sequence(m)
    graph.add_weighted_edges_from((u, v, w) for (u, v), w in zip(edges, ws))

    return graph


def save_apsp_to_cmatrix(graph: nx.DiGraph, mat):
    n = graph.number_of_nodes()
    distance_matrix = nx.floyd_warshall_numpy(graph)
    distance_matrix = np.nan_to_num(distance_matrix, posinf=INF)
    dmi = distance_matrix.astype(np.intc)
    for i, j in itertools.product(range(n), range(n)):
        mat[i * n + j] = ctypes.c_int(dmi[i][j])


def save_graph_to_cmatrix(graph: nx.DiGraph, mat):
    n = graph.number_of_nodes()
    for i, j in itertools.product(range(n), range(n)):
        mat[i * n + j] = INF
    for i, j, weight in graph.edges(data="weight", default=0):
        mat[i * n + j] = weight


def compare_cmatrices(a, b, n: int) -> bool:
    return all(
        a[i * n + j] == b[i * n + j] for i, j in itertools.product(range(n), range(n))
    )


def get_libparagraph():
    lib = ctypes.CDLL(ctypes.util.find_library("paragraph"), mode=ctypes.RTLD_GLOBAL)

    lib.pargph_alloc_matrix.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.pargph_alloc_matrix.restype = PINT

    lib.pargph_print_matrix.argtypes = [PINT, ctypes.c_int, ctypes.c_int]
    lib.pargph_print_matrix.restype = None

    lib.pargph_free_matrix.argtypes = [PINT]
    lib.pargph_free_matrix.restype = None

    lib.pargph_seq_floyd_warshall.argtypes = [PINT, PINT, ctypes.c_int]
    lib.pargph_seq_floyd_warshall.restype = None

    lib.pargph_par_floyd_warshall.argtypes = [PINT, PINT, ctypes.c_int]
    lib.pargph_par_floyd_warshall.restype = None

    return lib


def bench_algorithm(
    graph: nx.DiGraph, algo: Algorithm, warmup_iters: int, test_iters: int
) -> list[int]:
    lib = get_libparagraph()
    n = graph.number_of_nodes()
    c_n = ctypes.c_int(n)
    TOTAL_ITERS = warmup_iters + test_iters

    adj = lib.pargph_alloc_matrix(c_n, c_n)
    save_graph_to_cmatrix(graph, adj)

    test = lib.pargph_alloc_matrix(c_n, c_n)
    save_apsp_to_cmatrix(graph, test)

    dist = lib.pargph_alloc_matrix(c_n, c_n)

    if algo == Algorithm.SEQUENTIAL_FLOYD_WARSHALL:
        fn = lib.pargph_seq_floyd_warshall
    elif algo == Algorithm.PARALLEL_FLOYD_WARSHALL:
        fn = lib.pargph_par_floyd_warshall
    else:
        sys.exit(f"Algorithm provided not recognized {algo}")

    samples = []
    for i in range(TOTAL_ITERS):
        start = time.perf_counter_ns()
        fn(adj, dist, n)
        end = time.perf_counter_ns()
        elapsed = end - start

        if i == warmup_iters:
            if not compare_cmatrices(dist, test, n):
                print("Correct:\n")
                lib.pargph_print_matrix(test, c_n, c_n)
                print("Output:\n")
                lib.pargph_print_matrix(dist, c_n, c_n)
                sys.exit(f"Algorithm {algo} is incorrect")

        if i >= warmup_iters:
            print(f"Trial #{i - warmup_iters}: {elapsed} ns")
            samples.append(elapsed)

    lib.pargph_free_matrix(dist)
    lib.pargph_free_matrix(test)
    lib.pargph_free_matrix(adj)
    return samples


def run_benchmarks(
    # i/o
    filename: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.csv"),
    # iter
    warmup_iters: int = 100,
    test_iters: int = 100,
    # density
    min_density_perc: int = 10,
    max_density_perc: int = 100,
    density_perc_step: int = 10,
    # node range
    min_node_exp: int = 2,
    max_node_exp: int = 8,
    node_exp_scale: int = 2,
):
    if get_libparagraph():
        print("Paragraph is accessible to linker")
    else:
        sys.exit("Paragraph is inaccessible to linker")

    file = open(filename, mode="w", encoding="utf-8")
    writer = csv.writer(file)
    writer.writerow(["Nodes", "Edges", "Density", "Algorithm", "ElapsedNS"])

    for algo in [
        Algorithm.SEQUENTIAL_FLOYD_WARSHALL,
        Algorithm.PARALLEL_FLOYD_WARSHALL,
    ]:
        for e in range(min_node_exp, max_node_exp):
            n = node_exp_scale**e
            max_m = n * (n - 1)
            for percent_density in range(
                min_density_perc,
                max_density_perc + density_perc_step,
                density_perc_step,
            ):
                density = percent_density / 100.0
                m = int(max_m * density)
                print(
                    f"Starting trial: algo={algo.name}, n={n}, m={m} ({percent_density}% density)\n"
                )
                graph = generate_graph(n, m, 0)
                print("Benchmarking...")
                samples = bench_algorithm(graph, algo, warmup_iters, test_iters)
                for elapsed in enumerate(samples):
                    writer.writerow([n, m, density, algo.name, elapsed])
                print(f"Avg={sum(samples)/len(samples):,}")

    file.close()


if __name__ == "__main__":
    typer.run(run_benchmarks)
