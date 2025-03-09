#include <cstdlib>
#include <cstring>
#include <string>

extern "C"
{
    void* encode(void* stringData, void* stringKey)
    {
        std::string result = "Str: " + std::string(static_cast<char*>(stringData)) + ", key: " + std::string(static_cast<char*>(stringKey));

        void* buffer = std::malloc(result.size() * sizeof(char));
        std::memcpy(buffer, result.c_str(), result.size());

        return buffer;
    }

    void* decode(void* encodedData, void* stringKey)
    {
        std::string result = "Encoded: " + std::string(static_cast<char*>(encodedData)) + ", key: " + std::string(static_cast<char*>(stringKey));

        void* buffer = std::malloc(result.size() * sizeof(char));
        std::memcpy(buffer, result.c_str(), result.size());

        return buffer;
    }

    void* getRandomKey()
    {
        std::string result = "100:100";

        void* buffer = std::malloc(result.size() * sizeof(char));
        std::memcpy(buffer, result.c_str(), result.size());

        return buffer;
    }

    void freeMemory(void* ptr)
    {
        std::free(ptr);
    }
}
