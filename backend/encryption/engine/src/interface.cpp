#include <cstdlib>
#include <cstring>
#include <string>

#include "Engine.h"

Engine engine{};

extern "C"
{
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
