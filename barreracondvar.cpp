#include <iostream>
#include <pthread.h>
#include <vector>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <atomic>

using namespace std;

class CondVarBarrier {
    pthread_mutex_t mtx;
    pthread_cond_t cv;
    int counter;
    int cycle;
    int thread_count;
public:
    CondVarBarrier(int tc) : thread_count(tc), counter(0), cycle(0) {
        pthread_mutex_init(&mtx, NULL);
        pthread_cond_init(&cv, NULL);
    }
    ~CondVarBarrier() {
        pthread_mutex_destroy(&mtx);
        pthread_cond_destroy(&cv);
    }

    void wait() {
        pthread_mutex_lock(&mtx);
        int my_cycle = cycle;
        counter++;
        if (counter == thread_count) {
            cycle++;
            counter = 0;
            pthread_cond_broadcast(&cv);
        } else {
            while (cycle == my_cycle) {
                pthread_cond_wait(&cv, &mtx);
            }
        }
        pthread_mutex_unlock(&mtx);
    }
};

const int ROUNDS = 50;

struct ThreadArg {
    int thread_id;
    int thread_count;
    CondVarBarrier* barrier;
    vector<atomic<int>>* arrivals;
    atomic<bool>* verification_ok;
};

void* worker(void* arg) {
    ThreadArg* d = (ThreadArg*)arg;

    for (int r = 0; r < ROUNDS; r++) {
        (*d->arrivals)[r]++;
        d->barrier->wait();
        if ((*d->arrivals)[r].load() != d->thread_count) {
            *d->verification_ok = false;
        }
    }
    return NULL;
}

int main() {
    vector<int> lista_hilos = {2, 4, 8, 16, 32};

    ofstream csv("tiempos_barrera_condvar.csv");
    csv << "threads,tiempo,costo_us,verificado\n";

    for (int tc : lista_hilos) {
        CondVarBarrier barrier(tc);
        vector<pthread_t> threads(tc);
        vector<ThreadArg> args(tc);
        vector<atomic<int>> arrivals(ROUNDS);
        for (int r = 0; r < ROUNDS; r++) arrivals[r].store(0);
        atomic<bool> verification_ok(true);

        for (int i = 0; i < tc; i++) {
            args[i] = {i, tc, &barrier, &arrivals, &verification_ok};
        }

        auto start = chrono::high_resolution_clock::now();
        for (int i = 0; i < tc; i++) {
            pthread_create(&threads[i], NULL, worker, &args[i]);
        }
        for (int i = 0; i < tc; i++) {
            pthread_join(threads[i], NULL);
        }
        auto end = chrono::high_resolution_clock::now();

        chrono::duration<double> duration = end - start;
        double costo_us = (duration.count() / ROUNDS) * 1e6;

        csv << tc << ","<< fixed << setprecision(9) << duration.count() << ","<< fixed << setprecision(2) << costo_us << ","<< (verification_ok.load() ? "CORRECTO" : "ERROR") << "\n";
    }

    csv.close();
    return 0;
}

