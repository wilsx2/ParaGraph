from typing import Union
from enum import Enum
import networkx as nx
import numpy as np
import itertools
import ctypes.util
import ctypes
import random
import time
import sys

PPINT = ctypes.POINTER(ctypes.POINTER(ctypes.c_int))

class Algorithm(Enum):
    SEQUENTIAL_FLOYD_WARSHALL = 1

def random_u8_sequence(n: int):
    while n > 0:
        yield random.randint(0, 255)
        n -= 1


class GraphDescription:
    def __init__(self, n: int, m: int, seed: int):
        self.n = n
        self.m = m
        self.seed = seed

    def generate(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_nodes_from(range(self.n))

        possible_edges = list(itertools.permutations(range(self.n), 2))
        random.seed(self.seed)
        edges = random.sample(possible_edges, k=self.m)
        ws = random_u8_sequence(self.m)
        graph.add_edges_from((u, v, {'weight': w}) for (u, v), w in zip(edges, ws))

        return graph

def save_graph_to_cmatrix(graph: nx.DiGraph, mat, n: int):
    INF = np.iinfo(np.int32).max
    for i in range(n):
        for j in range(n):
            mat[i][j] = INF
    for i, j, weight in graph.edges(data='weight', default=0):
        mat[i][j] = weight

def get_libparagraph():
    lib = ctypes.CDLL(ctypes.util.find_library("paragraph"))

    lib.pargph_alloc_matrix.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.pargph_alloc_matrix.restype = PPINT

    lib.pargph_free_matrix.argtypes = [PPINT]
    lib.pargph_free_matrix.restype = None

    lib.pargph_seq_floyd_warshall.argtypes = [ctypes.c_int, PPINT, PPINT]
    lib.pargph_seq_floyd_warshall.restype = None

    return lib

def time_algorithm(graph: nx.DiGraph, algo: Algorithm) -> int:
    lib = get_libparagraph()
    n = graph.number_of_nodes()
    c_n = ctypes.c_int(n)

    adj = lib.pargph_alloc_matrix(c_n, c_n)
    save_graph_to_cmatrix(graph, adj, n)

    dist = lib.pargph_alloc_matrix(c_n, c_n)

    if algo == Algorithm.SEQUENTIAL_FLOYD_WARSHALL:
        start = time.perf_counter_ns()
        lib.pargph_seq_floyd_warshall(n, adj, dist)
        end = time.perf_counter_ns()
        elapsed = end - start
    else:
        sys.exit(f"Algorithm provided not recognized {algo}")

    lib.pargph_free_matrix(adj)
    lib.pargph_free_matrix(dist)
    return elapsed

if __name__ == "__main__":
    elapsed = time_algorithm(GraphDescription(8, 56, 0).generate(), Algorithm.SEQUENTIAL_FLOYD_WARSHALL)
    print(f"Running da algo took {elapsed} nanoseconds\n")
