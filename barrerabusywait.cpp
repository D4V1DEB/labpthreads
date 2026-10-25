#include <iostream>
#include <pthread.h>
#include <vector>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <atomic>

using namespace std;

class BusyWaitBarrier {
    pthread_mutex_t mtx;
    int counter;
    int thread_count;
    volatile int flag;
public:
    BusyWaitBarrier(int tc) : thread_count(tc), counter(0), flag(0) {
        pthread_mutex_init(&mtx, NULL);
    }
    ~BusyWaitBarrier() {
        pthread_mutex_destroy(&mtx);
    }

    void wait(int& my_flag) {
        my_flag = !my_flag;
        pthread_mutex_lock(&mtx);
        counter++;
        if (counter == thread_count) {
            counter = 0;
            flag = my_flag;
            pthread_mutex_unlock(&mtx);
        } else {
            pthread_mutex_unlock(&mtx);
            while (flag != my_flag); //
        }
    }
};

const int ROUNDS = 50;

struct ThreadArg {
    int thread_id;
    int thread_count;
    BusyWaitBarrier* barrier;
    vector<atomic<int>>* arrivals;
    atomic<bool>* verification_ok;
};

void* worker(void* arg) {
    ThreadArg* d = (ThreadArg*)arg;
    int my_flag = 0;

    for (int r = 0; r < ROUNDS; r++) {
        (*d->arrivals)[r]++;
        d->barrier->wait(my_flag);
        if ((*d->arrivals)[r].load() != d->thread_count) {
            *d->verification_ok = false;
        }
    }
    return NULL;
}

int main() {
    vector<int> lista_hilos = {2, 4, 8, 16, 32};

    ofstream csv("tiempos_barrera_busywait.csv");
    csv << "threads,tiempo,costo_us,verificado\n";

    for (int tc : lista_hilos) {
        BusyWaitBarrier barrier(tc);
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