#include <assert.h>
#include <dlfcn.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

int **square_matrix_alloc(int n) {
    // Can be refered to more tersely as "squalloc"
    size_t ptrs_size = n * sizeof(int *);
    size_t row_size = n * sizeof(int);
    int **mat = malloc(ptrs_size + n * row_size);
    for (int i = 0; i < n; ++i) {
        mat[i] = (int *)(mat + ptrs_size + i * row_size);
    }
    return mat;
}

int main(int argc, char *argv[]) {
    // Load implementation
    if (argc != 2) {
        fprintf(stderr, "Expected 2 arguments, received %d", argc);
        return EXIT_FAILURE;
    }

    void *handler = dlopen(argv[1], RTLD_NOW | RTLD_GLOBAL);
    if (handler == NULL) {
        fprintf(stderr, "%s\n", dlerror());
        return EXIT_FAILURE;
    }

    void (*floyd_warshall)(int, int **, int **);
    floyd_warshall = dlsym(handler, "floyd_warshall");
    if (floyd_warshall == NULL) {
        fprintf(stderr, "%s\n", dlerror());
        return EXIT_FAILURE;
    }

    // Set up matrices
    short n;
    read(STDIN_FILENO, &n, sizeof(n));

    int **adj = square_matrix_alloc(n);
    int **dist = square_matrix_alloc(n);
    size_t data_size = n * n * sizeof(int);

    read(STDIN_FILENO, adj[0], data_size);

    // Perform timed Floyd-Warshall
    time_t start, end;
    double elapsed;

    time(&start);
    floyd_warshall(n, adj, dist);
    time(&end);

    elapsed = difftime(end, start);

    // Output results + wall Time
    write(STDOUT_FILENO, dist[0], data_size);
    write(STDOUT_FILENO, &elapsed, sizeof(elapsed));

    // Clean up our resources
    free(dist);
    free(adj);
    dlclose(handler);

    return EXIT_SUCCESS;
}
