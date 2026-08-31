#include "paragraph.h"
#include <limits.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define N 6
#define INF INT_MAX


int main(int argc, char *argv[])
{
    int adj_data[N][N] = {
        {INF,INF,5  ,2  ,INF,INF},
        {INF,INF,INF,INF,8  ,INF},
        {INF,2  ,INF,INF,INF,INF},
        {1  ,INF,6  ,INF,INF,3  },
        {INF,INF,4  ,INF,INF,INF},
        {4  ,INF,INF,INF,INF,INF}
    };
    int *adj, *dist;
    adj = pargph_alloc_matrix(N, N);
    dist = pargph_alloc_matrix(N, N);
    memcpy(adj, adj_data, sizeof(adj_data));

    pargph_seq_floyd_warshall(adj, dist, N);

    printf("Adjacency Matrix\n");
    pargph_print_matrix(adj, N, N);
    printf("Distance Matrix\n");
    pargph_print_matrix(dist, N, N);

    free(adj);
    free(dist);
    return EXIT_SUCCESS;
}
