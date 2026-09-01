#ifndef PARGPH_H
#define PARGPH_H

#define PARGPH_INF (INT_MAX / 2 - 1)

#ifdef __cplusplus
extern "C" {
#endif

int *pargph_alloc_matrix(int m, int n);
void pargph_print_matrix(int *mat, int m, int n);
void pargph_free_matrix(int *mat);
void pargph_seq_floyd_warshall(int *adj, int *dist, int n);
void pargph_par_floyd_warshall(int *adj, int *dist, int n);

#ifdef __cplusplus
}
#endif

#endif
