#ifndef ENGINE_H
#define ENGINE_H

#include <random>
#include <string>
#include <vector>
#include <cstdint>

class Engine
{
public:
    Engine();

    std::string encode(std::string stringData, const std::string& key);
    std::string decode(const std::string& encodedData, const std::string& key);

    std::uint64_t predictEncodedSize(std::uint64_t dataSize);

    std::string generateRandomKey();

    std::uint64_t getMaxKeySize();

private:
    struct KeyData
    {
        int piOffsetLeftLimit;
        int piOffsetRightLimit;
        int digitsLeftLimit;
        int digitsRightLimit;
        int digitsShiftLeftLimit;
        int digitsShiftRightLimit;
        int shiftsBetweenQueries;
    };

    KeyData keyToData(std::string key);

    template <size_t blockSize>
    std::string encode_with_block_size(const std::string& stringData, const KeyData& keyData, bool decode);

    std::mt19937_64 m_randomEngine;
    
    std::uint64_t m_maxKeySize = 25; // maximum size of key

    int m_maxSizeDigits = 15; // digits used to store original message size in encoded message

    int m_queriesRelativeCount = 10; // how many queries will be performed for every data block

    int m_minInfoDigits = 10; // enough information to specify one bound of encoding query
    int m_maxInfoDigits = 19; // not more than max full digits of std::uint64_t (19)

    // possible shifts between queries information, co-prime to 2 and 5 to prevent repetition during overlapping
    std::vector<int> m_shifts{ 11, 13, 17, 19, 21, 23, 27, 29, 31, 33 };

    // odd numbers to balance queries
    std::vector<int> m_shiftsBetweenQueries{ 11, 13, 15, 17, 19, 21, 23, 25, 27, 29 };

    std::string m_piDigits{}; // pi digits obtained from server (10 millions)
};

#endif
