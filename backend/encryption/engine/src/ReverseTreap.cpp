#include "ReverseTreap.h"

#include <cstdlib>
#include <algorithm>
#include <iostream>

template <size_t blockSize>
ReverseTreap<blockSize>::ReverseTreap(const std::vector<ReverseTreap<blockSize>::DataBlock>& data)
{
	for (int i = 0; i < data.size(); i++)
	{
		m_root = this->insert(m_root, 0, i, new Node(data[i], rand() % s_topNodePriority));
	}
}

template <size_t blockSize>
ReverseTreap<blockSize>::Node::Node(const ReverseTreap<blockSize>::DataBlock& val, int priority) :
	val{ val },
	priority{ priority }
{
}

template <size_t blockSize>
void ReverseTreap<blockSize>::propagate(Node* node)
{
	if (!node)
	{
		return;
	}

	if (node->reverse)
	{
		std::swap(node->left, node->right);

		if (node->left)
		{
			node->left->reverse = !node->left->reverse;
		}
		if (node->right)
		{
			node->right->reverse = !node->right->reverse;
		}

		node->reverse = false;
	}
}

template <size_t blockSize>
typename ReverseTreap<blockSize>::Node* ReverseTreap<blockSize>::rightRotate(Node* y)
{
    Node* x = y->left;

	this->propagate(x);

	Node* t1 = x->left;
	Node* t2 = x->right;
	Node* t3 = y->right;

    x->right = y;
    y->left = t2;

	y->count = (t2 ? t2->count : 0) + (t3 ? t3->count : 0) + 1;
	x->count = (t1 ? t1->count : 0) + y->count + 1;

    return x;
}

template <size_t blockSize>
typename ReverseTreap<blockSize>::Node* ReverseTreap<blockSize>::leftRotate(Node* x)
{
	Node* y = x->right;

	this->propagate(y);

	Node* t1 = x->left;
	Node* t2 = y->left;
	Node* t3 = y->right;

    y->left = x;
    x->right = t2;

	x->count = (t1 ? t1->count : 0) + (t2 ? t2->count : 0) + 1;
	y->count = x->count + (t3 ? t3->count : 0) + 1;

    return y;
}

template <size_t blockSize>
typename ReverseTreap<blockSize>::Node* ReverseTreap<blockSize>::insert(Node* node, int k, int pos, Node* val)
{
	this->propagate(node);

	if (!node)
	{
		node = val;
	}
	else if (pos <= k + (node->left ? node->left->count : 0))
	{
		node->left = this->insert(node->left, k, pos, val);
		node->count++;

		if (node->left->priority > node->priority)
		{
			node = this->rightRotate(node);
		}
	}
	else
	{
		node->right = this->insert(node->right, k + (node->left ? node->left->count : 0) + 1, pos, val);
		node->count++;

		if (node->right->priority > node->priority)
		{
			node = this->leftRotate(node);
		}
	}

	return node;
}

template <size_t blockSize>
typename ReverseTreap<blockSize>::Node* ReverseTreap<blockSize>::erase(Node* node, int pos)
{
    this->propagate(node);

    if (pos < (node->left ? node->left->count : 0))
    {
        node->left = this->erase(node->left, pos);
        node->count--;

        return node;
    }
	if (pos > (node->left ? node->left->count : 0))
	{
		node->right = this->erase(node->right, pos - (node->left ? node->left->count : 0) - 1);\
		node->count--;

		return node;
	}
    if (!node->left)
    {
        Node* temp = node->right;
        node->right = nullptr;
        delete node;

        return temp;
    }
    if (!node->right)
    {
        Node* temp = node->left;
        node->left = nullptr;
        delete node;

        return temp;
    }
    if (node->left->priority < node->right->priority)
    {
        node = this->leftRotate(node);

        node->left = this->erase(node->left, pos);
        node->count--;

        return node;
    }

    node = this->rightRotate(node);

    node->right = this->erase(node->right, pos - (node->left ? node->left->count : 0) - 1);
    node->count--;

    return node;
}

template <size_t blockSize>
typename ReverseTreap<blockSize>::Node* ReverseTreap<blockSize>::split(int pos)
{
	m_root = this->insert(m_root, 0, pos, new Node(DataBlock{}, s_topNodePriority));

	Node* res = m_root->right;

	m_root->right = nullptr;
	m_root->count = (m_root->left ? m_root->left->count : 0) + 1;

	m_root = this->erase(m_root, pos);

	return res;
}

template <size_t blockSize>
void ReverseTreap<blockSize>::merge(Node* node)
{
	Node* tempRoot = new Node(DataBlock{}, s_topNodePriority);
	tempRoot->left = m_root;
	tempRoot->right = node;
	tempRoot->count = (tempRoot->left ? tempRoot->left->count : 0) + (tempRoot->right ? tempRoot->right->count : 0) + 1;

	int pos = tempRoot->left ? tempRoot->left->count : 0;
	m_root = this->erase(tempRoot, pos);
}

template <size_t blockSize>
void ReverseTreap<blockSize>::reverseRange(int l, int r)
{
	Node* rightPart = this->split(r + 1);
	Node* midPart = this->split(l);

	midPart->reverse = !midPart->reverse;

	this->merge(midPart);
	this->merge(rightPart);
}

template <size_t blockSize>
std::vector<typename ReverseTreap<blockSize>::DataBlock> ReverseTreap<blockSize>::getData()
{
	std::vector<DataBlock> data{};

	this->getDataFromNodes(m_root, data);

	return data;
}

template <size_t blockSize>
void ReverseTreap<blockSize>::getDataFromNodes(ReverseTreap::Node* node, std::vector<ReverseTreap<blockSize>::DataBlock>& data)
{
	this->propagate(node);

	if (!node)
	{
		return;
	}

	this->getDataFromNodes(node->left, data);

	data.push_back(node->val);

	this->getDataFromNodes(node->right, data);
}

template class ReverseTreap<1>; // 1 bit
template class ReverseTreap<8>; // 1 byte
template class ReverseTreap<64>; // 8 bytes
template class ReverseTreap<512>; // 64 bytes
template class ReverseTreap<4096>; // 512 bytes
template class ReverseTreap<32768>; // 4 kilobytes
