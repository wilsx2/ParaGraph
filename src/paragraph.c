#include "paragraph.h"
#include <assert.h>
#include <limits.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INF (PARGPH_INF)
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

#define BLOCK_SIZE 64

__attribute__((always_inline)) static inline void
block_floyd(int *a, int *b, int *c, int nk, int ni, int nj, int n) {
    nk = MIN(BLOCK_SIZE, n - nk * BLOCK_SIZE);
    ni = MIN(BLOCK_SIZE, n - ni * BLOCK_SIZE);
    nj = MIN(BLOCK_SIZE, n - nj * BLOCK_SIZE);

    for (int k = 0; k < nk; ++k) {
        for (int i = 0; i < ni; ++i) {
            for (int j = 0; j < nj; ++j) {
                c[i * n + j] = MIN(c[i * n + j], a[i * n + k] + b[k * n + j]);
            }
        }
    }
}

void pargph_par_floyd_warshall(int *adj, int *dist, int n) {
    assert(adj && dist);
    memcpy(dist, adj, n * n * sizeof(int));

    int B = (n + BLOCK_SIZE - 1) / BLOCK_SIZE;
#pragma omp parallel
    {
#pragma omp for
        for (int i = 0; i < n; ++i) {
            dist[i * n + i] = 0;
        }

        for (int k = 0; k < B; ++k) {
            // Pivot Block
            int *B_kk = &dist[k * n * BLOCK_SIZE + k * BLOCK_SIZE];
            block_floyd(B_kk, B_kk, B_kk, k, k, k, n);

#pragma omp for
            for (int j = 0; j < B; ++j) {
                if (j == k)
                    continue;
                int *B_kj = &dist[k * n * BLOCK_SIZE + j * BLOCK_SIZE];
                // Pivot Row
                block_floyd(B_kk, B_kj, B_kj, k, k, j, n);
            }

#pragma omp for
            for (int i = 0; i < B; ++i) {
                if (i == k)
                    continue;
                // Pivot Column
                int *B_ik = &dist[i * n * BLOCK_SIZE + k * BLOCK_SIZE];
                block_floyd(B_ik, B_kk, B_ik, i, k, k, n);

                // Inner blocks
                for (int j = 0; j < B; ++j) {
                    if (j == k)
                        continue;
                    int *B_ij = &dist[i * n * BLOCK_SIZE + j * BLOCK_SIZE];
                    int *B_kj = &dist[k * n * BLOCK_SIZE + j * BLOCK_SIZE];
                    block_floyd(B_ik, B_kj, B_ij, i, k, j, n);
                }
            }
        }
    }
}
