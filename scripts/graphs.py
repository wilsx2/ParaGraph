import random
import io
import multiprocessing as mp
import networkx as nx
import numpy as np
import numpy.typing as npt
from itertools import product

def generate_graph(n: int, density: float, seed: int) -> nx.DiGraph:
    random.seed(seed)
    graph = nx.DiGraph()
    graph.add_nodes_from(range(0, n))
    for i, j in product(range(n),range(n)):
        if random.random() < density:
            graph.add_edge(i, j, weight=random.randint(0, 255))
    return graph

def encode_graph_as_binary_adjacency_matrix(graph: nx.DiGraph) -> io.BytesIO:
    stream = io.BytesIO()

    n = graph.number_of_nodes()
    n_encoded = n.to_bytes(length=2, byteorder='big', signed=False)
    stream.write(n_encoded)

    INF = np.iinfo(np.uint32).max
    matrix = np.full((n, n), INF, dtype=np.uint32)
    for i, j, weight in graph.edges(data='weight', default=0):
        matrix[i,j] = weight

    stream.write(matrix.tobytes())
    return stream

def decode_apsp_from_binary_distance_matrix(stream: io.BytesIO) -> npt.NDArray[np.uint32]:
    n = int.from_bytes(stream.read(2), signed=False)
    flat = np.frombuffer(stream.getbuffer(), dtype=np.uint32)
    matrix = flat.reshape(n, n)
    return matrix
