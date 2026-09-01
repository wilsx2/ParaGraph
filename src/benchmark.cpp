#include "paragraph.h"
#include <benchmark/benchmark.h>
#include <boost/graph/adjacency_matrix.hpp>
#include <boost/pending/property.hpp>
#include <algorithm>
#include <generator>
#include <random>
#include <ranges>

using BoostDWG =
    boost::adjacency_matrix<boost::directedS, boost::no_property, int>;
using AdjacencyList = std::vector<std::tuple<int, int, int>>;

static auto random_u8_sequence(std::mt19937 gen) -> std::generator<int> {
    static std::uniform_int_distribution<int> distr(0, 255);
    for (;;) {
        co_yield distr(gen);
    }
}

static auto generate_graph(int n, int m, std::size_t seed) -> AdjacencyList {
    using namespace std::ranges::views;
    using std::ranges::sample;
    std::mt19937 gen;
    gen.seed(seed);

    auto edge_permutations =
        cartesian_product(iota(0, n), iota(0, n)) | filter([&](auto edge) {
            return std::get<0>(edge) != std::get<1>(edge);
        });
    auto edge_permutations_vec = to<std::vector>(edge_permutations);
    decltype(edge_permutations_vec) m_edges;
    sample(edge_permutations_vec, std::back_inserter(m_edges), m, gen);
    std::vector<int> us, vs;
    std::for_each(m_edges.begin(), m_edges.end(), [&us, &vs](const auto &edge) {
        us.emplace_back(std::get<0>(edge));
        vs.emplace_back(std::get<1>(edge));
    });
    auto ws = std::ranges::to<std::vector>(random_u8_sequence(gen) | take(m));
    return std::ranges::to<std::vector>(zip(us, vs, ws));
}

static void store_edges(BoostDWG &dwg, const AdjacencyList &edges) {
    for (auto &&[u, v, w] : edges) {
        boost::add_edge(u, v, w, dwg);
    }
}

static auto store_edges(int *adj_mat, int n, const AdjacencyList &edges) {
    for (auto &&[u, v, w] : edges) {
        adj_mat[u * n + v] = w;
    }
}

static auto compare_graphs(BoostDWG dwg, int *adj_mat, int n) {
    using namespace std::ranges::views;
    for (auto &&[u, v] : cartesian_product(iota(0, n), iota(0, n))) {
        auto dwg_adjacency = dwg.get_edge(u, v);
        auto mat_weight = adj_mat[u * n + v];

        auto agree_on_existence =
            (mat_weight == PARGPH_INF) == (!std::get<0>(dwg_adjacency));
        if (!agree_on_existence) {
            return false;
        }
        auto agree_on_weight = mat_weight == std::get<1>(dwg_adjacency);
        if (!agree_on_weight) {
            return false;
        }
    }
    return true;
}

template <auto F>
static void apsp(benchmark::State &state) {
    auto n = static_cast<int>(state.range(0));
    auto density_percent = static_cast<int>(state.range(1));
    auto m = static_cast<int>(n * static_cast<float>(density_percent) / 100.f);

    auto i = 0;
    auto hash = std::hash<int>();
    for (auto _ : state) {
        state.PauseTiming();
        auto adj = pargph_alloc_matrix(n, n);
        auto dist = pargph_alloc_matrix(n, n);

        auto seed = hash(i++);
        auto edges = generate_graph(n, m, seed);
        store_edges(adj, n, edges);

        state.ResumeTiming();
        F(adj, dist, n);

        state.PauseTiming();
        auto dwg = BoostDWG(n);
        store_edges(dwg, edges);
        assert(compare_graphs(dwg, adj, n));

        ::free(adj);
        ::free(dist);
    }
}
BENCHMARK_TEMPLATE(apsp, pargph_seq_floyd_warshall)
    ->ArgsProduct({{32, 64, 128, 256, 512, 1024, 2048}, {90}})
    ->Unit(benchmark::kMicrosecond);
BENCHMARK_TEMPLATE(apsp, pargph_par_floyd_warshall)
    ->ArgsProduct({{32, 64, 128, 256, 512, 1024, 2048}, {90}})
    ->Unit(benchmark::kMicrosecond);
