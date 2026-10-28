#include <iostream>
#include <pthread.h>
#include <semaphore.h>
#include <vector>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <atomic>

using namespace std;

class SemaphoreBarrier {
    sem_t count_sem;
    sem_t barrier_sem1;
    sem_t barrier_sem2;
    int counter;
    int thread_count;
public:
    SemaphoreBarrier(int tc) : thread_count(tc), counter(0) {
        sem_init(&count_sem, 0, 1);
        sem_init(&barrier_sem1, 0, 0);
        sem_init(&barrier_sem2, 0, 0);
    }
    ~SemaphoreBarrier() {
        sem_destroy(&count_sem);
        sem_destroy(&barrier_sem1);
        sem_destroy(&barrier_sem2);
    }

    void wait() {
        sem_wait(&count_sem);
        if (counter == thread_count - 1) {
            counter = 0;
            sem_post(&count_sem);
            for (int j = 0; j < thread_count - 1; j++) sem_post(&barrier_sem1);
        } else {
            counter++;
            sem_post(&count_sem);
            sem_wait(&barrier_sem1);
        }

        sem_wait(&count_sem);
        if (counter == thread_count - 1) {
            counter = 0;
            sem_post(&count_sem);
            for (int j = 0; j < thread_count - 1; j++) sem_post(&barrier_sem2);
        } else {
            counter++;
            sem_post(&count_sem);
            sem_wait(&barrier_sem2);
        }
    }
};

const int ROUNDS = 50;

struct ThreadArg {
    int thread_id;
    int thread_count;
    SemaphoreBarrier* barrier;
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

    ofstream csv("tiempos_barrera_semaforo.csv");
    csv << "threads,tiempo,costo_us,verificado\n";

    for (int tc : lista_hilos) {
        SemaphoreBarrier barrier(tc);
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

