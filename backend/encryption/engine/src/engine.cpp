#include "Engine.h"

Engine::Engine() :
    m_randomEngine(std::random_device{}())
{
}

std::string Engine::generateRandomKey()
{
    std::uniform_int_distribution<int> piDigitsDistribution(0, m_piDigits - 1);
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
