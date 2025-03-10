#include <fstream>
#include <iostream>
#include "Engine.h"

Engine::Engine() :
    m_randomEngine(std::random_device{}())
{
    std::ifstream("./backend/encryption/data/pi.txt") >> m_piDigits;
}

std::string Engine::encode(const std::string& stringData, const std::string& key)
{
    return stringData + key;
}

std::string Engine::decode(const std::string& encodedData, const std::string& key)
{
    return encodedData.substr(0, encodedData.size() - key.size());
}

std::string Engine::generateRandomKey()
{
    std::uniform_int_distribution<int> piDigitsDistribution(0, m_piDigits.size() - 1);
    std::uniform_int_distribution<int> infoDigits(0, m_maxInfoDigits - m_minInfoDigits);
    std::uniform_int_distribution<int> infoShiftIndex(0, m_shifts.size() - 1);
    std::uniform_int_distribution<int> infoShiftsBetweenQueriesIndex(0, m_shiftsBetweenQueries.size() - 1);

    return (
        std::to_string(piDigitsDistribution(m_randomEngine))
        + ":" + std::to_string(piDigitsDistribution(m_randomEngine))
        + ":" + std::to_string(infoDigits(m_randomEngine))
        + ":" + std::to_string(infoDigits(m_randomEngine))
        + ":" + std::to_string(infoShiftIndex(m_randomEngine))
        + ":" + std::to_string(infoShiftIndex(m_randomEngine))
        + ":" + std::to_string(infoShiftsBetweenQueriesIndex(m_randomEngine))
    );
}
