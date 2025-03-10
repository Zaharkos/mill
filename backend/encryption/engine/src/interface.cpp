#include <cstdlib>
#include <cstring>
#include <string>

#include "Engine.h"

Engine engine{};

extern "C"
{
    void* encode(const char* stringData, const char* key)
    {
        std::string result = engine.encode(stringData, key);

        void* buffer = std::malloc((result.size() + 1) * sizeof(char));
        std::strcpy(static_cast<char*>(buffer), result.c_str());

        return buffer;
    }

    void* decode(const char* encodedData, const char* key)
    {
        std::string result = engine.decode(encodedData, key);

        void* buffer = std::malloc((result.size() + 1) * sizeof(char));
        std::strcpy(static_cast<char*>(buffer), result.c_str());

        return buffer;
    }

    void* generateRandomKey()
    {
        std::string result = engine.generateRandomKey();

        void* buffer = std::malloc((result.size() + 1) * sizeof(char));
        std::strcpy(static_cast<char*>(buffer), result.c_str());

        return buffer;
    }

    void freeMemory(void* ptr)
    {
        std::free(ptr);
    }
}
