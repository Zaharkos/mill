#include <fstream>
#include <memory>
#include <algorithm>

#include "ReverseTreap.h"

#include "Engine.h"

Engine::Engine() :
    m_randomEngine(std::random_device{}())
{
    std::ifstream("./backend/encryption/data/pi.txt") >> m_piDigits;
}

std::string Engine::encode(std::string stringData, const std::string& key)
{
    KeyData keyData = keyToData(key);

    std::string sizePref = std::to_string(stringData.size());
    sizePref = std::string(m_maxSizeDigits - sizePref.size(), '0') + sizePref;
    stringData = sizePref + stringData;

    if (stringData.size() < (1 << 17)) // <= 128 KB
    {
        return this->encode_with_block_size<8>(stringData, keyData, false);
    }
    if (stringData.size() < (1 << 20)) // <= 1 MB
    {
        return this->encode_with_block_size<64>(stringData + std::string(8 - stringData.size() % 8, '0'), keyData, false);
    }
    if (stringData.size() < (1 << 23)) // <= 8 MB
    {
        return this->encode_with_block_size<512>(stringData + std::string(64 - stringData.size() % 64, '0'), keyData, false);
    }
    if (stringData.size() < (1 << 26)) // <= 64 MB
    {
        return this->encode_with_block_size<4096>(stringData + std::string(512 - stringData.size() % 512, '0'), keyData, false);
    }

    return this->encode_with_block_size<32768>(stringData + std::string(4096 - stringData.size() % 4096, '0'), keyData, false);
}

std::string Engine::decode(const std::string& encodedData, const std::string& key)
{
    KeyData keyData = keyToData(key);

    std::string res{};

    if (encodedData.size() <= (1 << 17)) // <= 128 KB
    {
        res = this->encode_with_block_size<8>(encodedData, keyData, true);
    }
    else if (encodedData.size() <= (1 << 20)) // <= 1 MB
    {
        res = this->encode_with_block_size<64>(encodedData, keyData, true);
    }
    else if (encodedData.size() <= (1 << 23)) // <= 8 MB
    {
        res = this->encode_with_block_size<512>(encodedData, keyData, true);
    }
    else if (encodedData.size() <= (1 << 26)) // <= 64 MB
    {
        res = this->encode_with_block_size<4096>(encodedData, keyData, true);
    }
    else
    {
        res = this->encode_with_block_size<32768>(encodedData, keyData, true);
    }

    size_t resSize = std::stoull(res.substr(0, m_maxSizeDigits));

    return res.substr(m_maxSizeDigits, resSize);
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

Engine::KeyData Engine::keyToData(std::string key)
{
    KeyData keyData;

    keyData.piOffsetLeftLimit = std::stoi(key.substr(0, key.find(":")));
    key = key.substr(key.find(":") + 1);
    keyData.piOffsetRightLimit = std::stoi(key.substr(0, key.find(":")));
    key = key.substr(key.find(":") + 1);
    keyData.digitsLeftLimit = std::stoi(key.substr(0, key.find(":"))) + m_minInfoDigits;
    key = key.substr(key.find(":") + 1);
    keyData.digitsRightLimit = std::stoi(key.substr(0, key.find(":"))) + m_minInfoDigits;
    key = key.substr(key.find(":") + 1);
    keyData.digitsShiftLeftLimit = m_shifts[std::stoi(key.substr(0, key.find(":")))];
    key = key.substr(key.find(":") + 1);
    keyData.digitsShiftRightLimit = m_shifts[std::stoi(key.substr(0, key.find(":")))];
    key = key.substr(key.find(":") + 1);
    keyData.shiftsBetweenQueries = m_shiftsBetweenQueries[std::stoi(key)];

    return keyData;
}

template <size_t blockSize>
std::string Engine::encode_with_block_size(const std::string& stringData, const KeyData& key, bool decode)
{
    std::vector<typename ReverseTreap<blockSize>::DataBlock> data(stringData.size() * 8 / blockSize);
    for (int i = 0; i < data.size(); i++)
    {
        for (int j = 0; j < blockSize; j++)
        {
            data[i][j] = stringData[(i * blockSize + j) / 8] & (1 << ((i * blockSize + j) % 8));
        }
    }

    int dataSize = data.size();
    int queriesCount = dataSize * m_queriesRelativeCount;
    ReverseTreap<blockSize> reverseTreap(std::move(data));

    std::vector<std::pair<size_t, int>> leftLimitInfo(queriesCount);
    int currPtr = key.digitsLeftLimit;
    for (int i = 0; i < queriesCount; i++)
    {
        leftLimitInfo[i] = { std::stoull(m_piDigits.substr(currPtr, key.digitsLeftLimit)), i % dataSize };
        currPtr = (currPtr + key.digitsShiftLeftLimit) % (m_piDigits.size() - key.digitsLeftLimit);
    }
    std::sort(leftLimitInfo.begin(), leftLimitInfo.end());

    std::vector<int> rightLimitInfo(queriesCount);
    currPtr = key.digitsRightLimit;
    for (int i = 0; i < queriesCount; i++)
    {
        rightLimitInfo[i] = std::stoull(m_piDigits.substr(currPtr, key.digitsRightLimit)) % dataSize;
        currPtr = (currPtr + key.digitsShiftRightLimit) % (m_piDigits.size() - key.digitsRightLimit);
    }

    int shiftsBetweenQueriesInterval = std::ceil((double)queriesCount / (key.shiftsBetweenQueries + 1));

    for (int i = decode ? queriesCount - 1 : 0; decode ? i >= 0 : i < queriesCount; decode ? i-- : i++)
    {
        bool makeShift = i && i % shiftsBetweenQueriesInterval == 0 && dataSize > 1;
        if (makeShift && !decode)
        {
            reverseTreap.reverseRange(0, dataSize - 1);
            reverseTreap.reverseRange(0, dataSize / 2 - 1);
            reverseTreap.reverseRange(dataSize / 2, dataSize - 1);
        }

        if (leftLimitInfo[i].second > rightLimitInfo[i])
        {
            std::swap(leftLimitInfo[i].second, rightLimitInfo[i]);
        }
        reverseTreap.reverseRange(leftLimitInfo[i].second, rightLimitInfo[i]);

        if (makeShift && decode)
        {
            reverseTreap.reverseRange(0, dataSize / 2 - 1);
            reverseTreap.reverseRange(dataSize / 2, dataSize - 1);
            reverseTreap.reverseRange(0, dataSize - 1);
        }
    }

    data = reverseTreap.getData();
    std::string res(stringData.size(), 0);

    for (int i = 0; i < res.size(); i++)
    {
        for (int j = 0; j < 8; j++)
        {
            stringData[(i * blockSize + j) / 8] & (1 << (j % 8));
            res[i] |= data[(i * 8 + j) / blockSize][(i * 8 + j) % blockSize] * (1 << j);
        }
    }

    return res;
}
