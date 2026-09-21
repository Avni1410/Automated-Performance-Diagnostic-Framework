// race_condition.cpp
//
// Demonstrates a classic race condition: two threads incrementing
// a shared counter without synchronization.
//
// Expected result: 2,000,000
// Actual result: usually LESS because counter++ is not atomic.

#include <iostream>
#include <thread>

long counter = 0;

void increment_counter(int times) {
    for (int i = 0; i < times; i++) {
        counter++;
    }
}

int main() {
    const int increments_per_thread = 1000000;

    std::thread t1(increment_counter, increments_per_thread);
    std::thread t2(increment_counter, increments_per_thread);

    t1.join();
    t2.join();

    std::cout << "Expected counter value: "
              << (2 * increments_per_thread) << std::endl;

    std::cout << "Actual counter value:   "
              << counter << std::endl;

    return 0;
}
