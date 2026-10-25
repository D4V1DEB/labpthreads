#include <iostream>
#include <chrono>
#include <vector>
#include <fstream>
#include <iomanip>

using namespace std;

void multiplicar_secuencial(int n, const vector<double>& A, const vector<double>& x, vector<double>& y) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        int row_offset = i * n;
        for (int j = 0; j < n; j++) {
            sum += A[row_offset + j] * x[j];
        }
        y[i] = sum;
    }
}

int main() {
    vector<int> tamanos = {2000, 4000, 6000, 8000, 10000};

    ofstream csv("tiempos_matvec_secuencial.csv");
    csv << "n,tiempo\n";

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

        auto start_time = chrono::high_resolution_clock::now();
        multiplicar_secuencial(n, A, x, y);
        auto end_time = chrono::high_resolution_clock::now();

        chrono::duration<double> duration = end_time - start_time;

        csv << n << "," << fixed << setprecision(9) << duration.count() << "\n";
    }

    csv.close();
    return 0;
}