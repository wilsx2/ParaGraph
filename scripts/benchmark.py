from typing import Union
from enum import Enum
from datetime import datetime
import networkx as nx
import numpy as np
import itertools
import ctypes.util
import ctypes
import random
import time
import csv
import sys

PPINT = ctypes.POINTER(ctypes.POINTER(ctypes.c_int))

class Algorithm(Enum):
    SEQUENTIAL_FLOYD_WARSHALL = 1

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
    distance_matrix = np.nan_to_num(distance_matrix, posinf=np.iinfo(np.intc).max)
    dmi = distance_matrix.astype(np.intc)
    for i, j in itertools.product(range(n), range(n)):
        mat[i][j] = ctypes.c_int(dmi[i][j])

def save_graph_to_cmatrix(graph: nx.DiGraph, mat):
    n = graph.number_of_nodes()
    INF = np.iinfo(np.int32).max
    for i, j in itertools.product(range(n), range(n)):
            mat[i][j] = INF
    for i, j, weight in graph.edges(data='weight', default=0):
        mat[i][j] = weight


def compare_cmatrices(a, b, n: int) -> bool:
    return all(a[i][j] == b[i][j] for i, j in itertools.product(range(n), range(n)))

def get_libparagraph():
    lib = ctypes.CDLL(ctypes.util.find_library("paragraph"), mode=ctypes.RTLD_GLOBAL)

    lib.pargph_alloc_matrix.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.pargph_alloc_matrix.restype = PPINT

    lib.pargph_print_matrix.argtypes = [PPINT, ctypes.c_int, ctypes.c_int]
    lib.pargph_print_matrix.restype = None

    lib.pargph_free_matrix.argtypes = [PPINT]
    lib.pargph_free_matrix.restype = None

    lib.pargph_seq_floyd_warshall.argtypes = [PPINT, PPINT, ctypes.c_int]
    lib.pargph_seq_floyd_warshall.restype = None

    return lib

def time_algorithm(graph: nx.DiGraph, algo: Algorithm) -> int:
    lib = get_libparagraph()
    n = graph.number_of_nodes()
    c_n = ctypes.c_int(n)

    adj = lib.pargph_alloc_matrix(c_n, c_n)
    save_graph_to_cmatrix(graph, adj)

    dist = lib.pargph_alloc_matrix(c_n, c_n)

    if algo == Algorithm.SEQUENTIAL_FLOYD_WARSHALL:
        start = time.perf_counter_ns()
        lib.pargph_seq_floyd_warshall(adj, dist, n)
        end = time.perf_counter_ns()
        elapsed = end - start
    else:
        sys.exit(f"Algorithm provided not recognized {algo}")

    test = lib.pargph_alloc_matrix(c_n, c_n)
    save_apsp_to_cmatrix(graph, test)


    if not compare_cmatrices(dist, test, n):
        print("Correct:\n")
        lib.pargph_print_matrix(test, c_n, c_n)
        print("Output:\n")
        lib.pargph_print_matrix(dist, c_n, c_n)
        sys.exit(f"Algorithm {algo} is incorrect")

    lib.pargph_free_matrix(test)
    lib.pargph_free_matrix(dist)
    lib.pargph_free_matrix(adj)
    return elapsed

if __name__ == "__main__":
    WARMUP_ITERS = 10
    TEST_ITERS = 100
    TOTAL_ITERS = WARMUP_ITERS + TEST_ITERS

    if(get_libparagraph()):
        print("Paragraph is accessible to linker")
    else:
        sys.exit("Paragraph is inaccessible to linker")

    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.csv")
    file = open(filename, mode='w', encoding='utf-8')
    writer = csv.writer(file)

    for algo in [Algorithm.SEQUENTIAL_FLOYD_WARSHALL]:
        for e in range(2, 8):
            n = 2**e
            max_m = n*(n-1)
            for percent_density in range(10, 100 + 10, 10):
                m = int(max_m * (percent_density / 100.0))
                print(f"Starting trial: n={n}, m={m} ({percent_density}% density)\n")
                graph = generate_graph(n, m, 0)
                print("Warming up...")
                total = 0
                for i in range(0, TOTAL_ITERS):
                    elapsed = time_algorithm(graph, algo)
                    total += elapsed
                    if i >= WARMUP_ITERS:
                        print(f"Trial #{i-WARMUP_ITERS}: {elapsed} ns")
                    writer.writerow([n,m,elapsed])
                print(f"Avg={total/TEST_ITERS}")

    file.close()
