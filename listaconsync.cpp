#include <iostream>
#include <pthread.h>
#include <chrono>
#include <vector>
#include <fstream>
#include <iomanip>

using namespace std;

struct Node {
    int val;
    Node* next;
    Node(int v, Node* n = nullptr) : val(v), next(n) {}
};

Node* head = nullptr;
pthread_mutex_t list_mutex = PTHREAD_MUTEX_INITIALIZER;

void insert_node(int val) {
    pthread_mutex_lock(&list_mutex);
    Node* new_node = new Node(val, head);
    head = new_node;
    pthread_mutex_unlock(&list_mutex);
}

bool search_node(int val) {
    pthread_mutex_lock(&list_mutex);
    Node* curr = head;
    while (curr) {
        if (curr->val == val) {
            pthread_mutex_unlock(&list_mutex);
            return true;
        }
        curr = curr->next;
    }
    pthread_mutex_unlock(&list_mutex);
    return false;
}

bool delete_node(int val) {
    pthread_mutex_lock(&list_mutex);
    Node* curr = head;
    Node* prev = nullptr;
    while (curr && curr->val != val) {
        prev = curr;
        curr = curr->next;
    }
    if (!curr) {
        pthread_mutex_unlock(&list_mutex);
        return false;
    }
    if (!prev) head = curr->next;
    else prev->next = curr->next;
    delete curr;
    pthread_mutex_unlock(&list_mutex);
    return true;
}

struct WorkerArg {
    int id;
    int n_ins;
    int n_del;
    int n_search;
};

void* worker(void* arg) {
    WorkerArg* a = (WorkerArg*)arg;
    int base = a->id * 100000;

    for (int i = 0; i < a->n_ins; i++) {
        insert_node(base + i);
    }
    for (int i = 0; i < a->n_del; i++) {
        delete_node(base + i);
    }
    for (int i = a->n_del; i < a->n_del + a->n_search; i++) {
        search_node(base + i);
    }

    return NULL;
}

void liberar_lista() {
    pthread_mutex_lock(&list_mutex);
    Node* curr = head;
    while (curr) {
        Node* temp = curr;
        curr = curr->next;
        delete temp;
    }
    head = nullptr;
    pthread_mutex_unlock(&list_mutex);
}

int contar_nodos() {
    pthread_mutex_lock(&list_mutex);
    int count = 0;
    Node* curr = head;
    while (curr) {
        count++;
        curr = curr->next;
    }
    pthread_mutex_unlock(&list_mutex);
    return count;
}

int main() {
    vector<int> lista_hilos = {2, 4, 8, 16, 32};
    const int N_INS = 2000;
    const int N_DEL = 500;
    const int N_SEARCH = 1000;

    ofstream csv("tiempos_lista_con_sync.csv");
    csv << "threads,ops_totales,tiempo,nodos_esperados,nodos_reales,nodos_perdidos,consistente\n";

    for (int num_threads : lista_hilos) {
        liberar_lista();

        vector<pthread_t> threads(num_threads);
        vector<WorkerArg> args(num_threads);
        long long ops_totales = (long long)num_threads * (N_INS + N_DEL + N_SEARCH);
        int nodos_esperados = num_threads * (N_INS - N_DEL);

        auto start_time = chrono::high_resolution_clock::now();

        for (int i = 0; i < num_threads; i++) {
            args[i] = {i, N_INS, N_DEL, N_SEARCH};
            pthread_create(&threads[i], NULL, worker, &args[i]);
        }

        for (int i = 0; i < num_threads; i++) {
            pthread_join(threads[i], NULL);
        }

        auto end_time = chrono::high_resolution_clock::now();
        chrono::duration<double> duration = end_time - start_time;

        int nodos_reales = contar_nodos();
        int nodos_perdidos = nodos_esperados - nodos_reales;

        csv << num_threads << "," << ops_totales << "," << fixed << setprecision(9) << duration.count() << "," << nodos_esperados << "," << nodos_reales << "," << nodos_perdidos << "," << (nodos_perdidos == 0 ? "SI" : "NO") << "\n";
    }

    liberar_lista();
    pthread_mutex_destroy(&list_mutex);
    csv.close();
    return 0;
}