#include <iostream>
#include <pthread.h>
#include <chrono>
#include <vector>
#include <fstream>
#include <iomanip>

using namespace std;

struct ThreadData {
    int start_row;
    int end_row;
    int n;
    const double* A;
    const double* x;
    double* y;
};

void* multiplicar_filas(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    int n = data->n;
    const double* A = data->A;
    const double* x = data->x;
    double* y = data->y;

    for (int i = data->start_row; i < data->end_row; i++) {
        double sum = 0.0;
        int row_offset = i * n;
        for (int j = 0; j < n; j++) {
            sum += A[row_offset + j] * x[j];
        }
        y[i] = sum;
    }

    return NULL;
}

int main() {
    vector<int> tamanos = {2000, 4000, 6000, 8000, 10000};
    vector<int> lista_hilos = {2, 4, 8, 16, 32};

    ofstream csv("tiempos_matvec_pthreads.csv");
    csv << "n,threads,tiempo\n";

    for (int n : tamanos) {
        vector<double> A((size_t)n * n);
        vector<double> x(n);
        vector<double> y(n, 0.0);

        for (int i = 0; i < n; i++) {
            x[i] = (i % 5) + 1.0;
            int offset = i * n;
            for (int j = 0; j < n; j++) {
                A[offset + j] = ((i + j) % 10) + 1.0;
            }
        }

        for (int num_threads : lista_hilos) {
            vector<pthread_t> threads(num_threads);
            vector<ThreadData> thread_data(num_threads);
            int chunk_size = n / num_threads;

            auto start_time = chrono::high_resolution_clock::now();

            for (int i = 0; i < num_threads; i++) {
                thread_data[i].start_row = i * chunk_size;
                thread_data[i].end_row = (i == num_threads - 1) ? n : (i + 1) * chunk_size;
                thread_data[i].n = n;
                thread_data[i].A = A.data();
                thread_data[i].x = x.data();
                thread_data[i].y = y.data();

                pthread_create(&threads[i], NULL, multiplicar_filas, &thread_data[i]);
            }

            for (int i = 0; i < num_threads; i++) {
                pthread_join(threads[i], NULL);
            }

            auto end_time = chrono::high_resolution_clock::now();
            chrono::duration<double> duration = end_time - start_time;

            csv << n << "," << num_threads << "," << fixed << setprecision(9) << duration.count() << "\n";
        }
    }

    csv.close();
    return 0;
}