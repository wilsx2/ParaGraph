#ifndef PARAGRAPH_H
#define PARAGRAPH_H

int **pargph_alloc_matrix(int m, int n);
void pargph_free_matrix(int **mat);
void pargph_seq_floyd_warshall(int, int **, int **);

#endif
