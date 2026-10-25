#include <iostream>
#include <pthread.h>
#include <chrono>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>

using namespace std;

struct ThreadData {
    long long start;
    long long end;
    double local_sum;
};

void* calcular_pi_hilo(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    double local_sum = 0.0;
    
    double factor = (data->start % 2 == 0) ? 1.0 : -1.0;
    
    for (long long i = data->start; i < data->end; i++) {
        local_sum += factor / (2.0 * i + 1.0);
        factor = -factor;
    }
    
    data->local_sum = local_sum;
    return NULL;
}

double ejecutar_pthreads(long long n, int num_threads, double& out_pi, double& out_error) {
    vector<pthread_t> threads(num_threads);
    vector<ThreadData> thread_data(num_threads);
    long long chunk_size = n / num_threads;

    auto start_time = chrono::high_resolution_clock::now();

    for (int i = 0; i < num_threads; i++) {
        thread_data[i].start = i * chunk_size;
        thread_data[i].end = (i == num_threads - 1) ? n : (i + 1) * chunk_size;
        thread_data[i].local_sum = 0.0;

        pthread_create(&threads[i], NULL, calcular_pi_hilo, &thread_data[i]);
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    double global_sum = 0.0;
    for (int i = 0; i < num_threads; i++) {
        global_sum += thread_data[i].local_sum;
    }

    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> duration = end_time - start_time;

    out_pi = 4.0 * global_sum;
    out_error = std::abs(out_pi - M_PI);

    return duration.count();
}

int main() {
    vector<long long> tamanos = {1000000LL, 10000000LL, 100000000LL, 1000000000LL};
    vector<int> lista_hilos = {2, 4, 8, 16, 32};

    ofstream csv("tiempos_pthreads.csv");
    csv << "n,threads,tiempo,pi_calculado,error\n";

    for (long long n : tamanos) {
        for (int hilos : lista_hilos) {
            double pi = 0.0, error = 0.0;
            double tiempo = ejecutar_pthreads(n, hilos, pi, error);
            csv << n << "," << hilos << "," << fixed << setprecision(9) << tiempo << "," << setprecision(15) << pi << "," << scientific << error << "\n";
        }
    }

    csv.close();
    return 0;
}