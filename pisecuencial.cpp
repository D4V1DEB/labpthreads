#include <iostream>
#include <chrono>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>

using namespace std;

double calcular_pi_secuencial(long long n) {
    double factor = 1.0;
    double sum = 0.0;
    
    for (long long i = 0; i < n; i++) {
        sum += factor / (2.0 * i + 1.0);
        factor = -factor;
    }
    
    return 4.0 * sum;
}

int main() {
    vector<long long> tamanos = {1000000LL, 10000000LL, 100000000LL, 1000000000LL};

    ofstream csv("tiempos_secuencial.csv");
    csv << "n,tiempo,pi_calculado,error\n";

    for (long long n : tamanos) {
        auto start_time = chrono::high_resolution_clock::now();
        double pi = calcular_pi_secuencial(n);
        auto end_time = chrono::high_resolution_clock::now();

        chrono::duration<double> duration = end_time - start_time;
        double error = std::abs(pi - M_PI);

        csv << n << "," << fixed << setprecision(9) << duration.count() << "," << setprecision(15) << pi << "," << scientific << error << "\n";
    }

    csv.close();
    return 0;
}