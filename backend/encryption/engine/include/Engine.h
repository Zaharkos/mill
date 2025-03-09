#ifndef ENGINE_H
#define ENGINE_H

#include <random>
#include <string>
#include <vector>

class Engine
{
public:
    Engine();

    std::string generateRandomKey();

private:
    std::mt19937_64 m_randomEngine;

    int m_piDigits = 10000000; // number of pi digits stored on server

    int m_minInfoDigits = 10; // enough information to specify one bound of encoding query
    int m_maxInfoDigits = 19; // not more than max full digits of std::uint64_t (19)

    // possible shifts between queries information, primes to prevent repetition during overlapping
    std::vector<int> m_shifts{ 7, 11, 13, 17, 19, 23, 29, 31, 37, 39 };

    // odd numbers to balance queries
    std::vector<int> m_shiftsBetweenQueries{ 1, 3, 5, 7, 9, 11, 13, 15, 17, 19 };
};

#endif
