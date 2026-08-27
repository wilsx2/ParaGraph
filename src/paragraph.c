#include "paragraph.h"
#include <assert.h>
#include <limits.h>
#include <memory.h>
#include <stdlib.h>
#include <string.h>

#define INF INT_MAX

int **pargph_alloc_matrix(int m, int n) {
    size_t ptrs_size = m * sizeof(int *);
    size_t row_size = n * sizeof(int);
    int **mat = malloc(ptrs_size + m * row_size);
    if (!mat)
        return NULL;
    char *data = (char *)mat + ptrs_size;
    for (int i = 0; i < m; ++i) {
        mat[i] = (int *)(data + i * row_size);
    }
    return mat;
}

void pargph_free_matrix(int **mat) { free(mat); }

void pargph_seq_floyd_warshall(int n, int **adj, int **dist) {
    assert(adj && dist);

    for (int i = 0; i < n * n; ++i)
        dist[0][i] = INF;

    for (int i = 0; i < n; ++i) {
        dist[i][i] = 0;
    }

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (adj[i][j] < INF) {
                dist[i][j] = adj[i][j];
            }
        }
    }

    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (dist[i][k] < INF && dist[k][j] < INF &&
                    dist[i][j] > dist[i][k] + dist[k][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
}
