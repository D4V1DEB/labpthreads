#include <iostream>
#include <chrono>
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
    long long n = 10000000;

    auto start_time = chrono::high_resolution_clock::now();
    double pi = calcular_pi_secuencial(n);
    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> duration = end_time - start_time;
    
    cout.precision(15);
    cout << "pi- " << pi << endl;
    cout << "tiempo- " << duration.count() << endl;
    return 0;
}