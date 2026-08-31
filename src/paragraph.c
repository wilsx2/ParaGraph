#include "paragraph.h"
#include <assert.h>
#include <limits.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INF (INT_MAX / 2 - 1)
#define MIN(a, b) (((a) < (b)) ? (a) : (b))

int *pargph_alloc_matrix(int m, int n) { return malloc(m * n * sizeof(int)); }

void pargph_print_matrix(int *mat, int m, int n) {
    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < n; ++j) {
            if (mat[i * n + j] == INF)
                printf("INF ");
            else
                printf("%3d ", mat[i * n + j]);
        }
        printf("\n");
    }
}

void pargph_free_matrix(int *mat) { free(mat); }

void pargph_seq_floyd_warshall(int *adj, int *dist, int n) {
    assert(adj && dist);
    memcpy(dist, adj, n * n * sizeof(int));

    for (int i = 0; i < n; ++i) {
        dist[i * n + i] = 0;
    }

    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                dist[i * n + j] =
                    MIN(dist[i * n + j], dist[i * n + k] + dist[k * n + j]);
            }
        }
    }
}

void pargph_par_floyd_warshall(int *adj, int *dist, int n) {
    assert(adj && dist);
    memcpy(dist, adj, n * n * sizeof(int));

#pragma omp parallel
    {
#pragma omp for
        for (int i = 0; i < n; ++i) {
            dist[i * n + i] = 0;
        }

        for (int k = 0; k < n; ++k) {
#pragma omp for collapse(2)
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < n; ++j) {
                    dist[i * n + j] =
                        MIN(dist[i * n + j], dist[i * n + k] + dist[k * n + j]);
                }
            }
        }
    }
}
