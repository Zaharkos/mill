#include <cstdlib>
#include <cstring>

#include "Engine.h"

Engine engine{};

extern "C"
{
    std::uint64_t encode(const char* stringDataBuffer, size_t stringDataSize, const char* key, char* resBuf)
    {
        std::string stringData(stringDataBuffer, stringDataBuffer + stringDataSize);

        std::string result = engine.encode(stringData, key);

        std::memcpy(resBuf, result.c_str(), result.size());

        return result.size();
    }

    std::uint64_t decode(const char* encodedDataBuffer, size_t encodedDataSize, const char* key, char* resBuf)
    {
        std::string encodedData(encodedDataBuffer, encodedDataBuffer + encodedDataSize);

        std::string result = engine.decode(encodedData, key);

        std::memcpy(resBuf, result.c_str(), result.size());

        return result.size();
    }

    std::uint64_t generateRandomKey(char* resBuf)
    {
        std::string result = engine.generateRandomKey();

        std::memcpy(resBuf, result.c_str(), result.size());

        return result.size();
    }

    std::uint64_t getMaxKeySize()
    {
        return engine.getMaxKeySize();
    }

    std::uint64_t predictEncodedSize(std::uint64_t dataSize)
    {
        return engine.predictEncodedSize(dataSize);
    }
}
