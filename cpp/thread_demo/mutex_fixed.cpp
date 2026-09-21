// mutex_fixed.cpp
//
// Fixes the race condition from race_condition.cpp by protecting
// the shared counter with a mutex.

#include <iostream>
#include <thread>
#include <mutex>

long counter = 0;

std::mutex counter_mutex;

void increment_counter(int times) {
    for (int i = 0; i < times; i++) {
        std::lock_guard<std::mutex> lock(counter_mutex);
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
