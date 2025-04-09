#ifndef REVERSE_TREAP_H
#define REVERSE_TREAP_H

#include <vector>
#include <bitset>

template <size_t blockSize>
class ReverseTreap
{
public:
	using DataBlock = std::bitset<blockSize>;

	ReverseTreap(const std::vector<DataBlock>& data);

	void reverseRange(int l, int r);

	std::vector<DataBlock> getData();

private:
	struct Node
	{
		Node(const DataBlock& val, int priority);

		DataBlock val;
		int priority;
		bool reverse = false;
		int count = 1;

		Node* left = nullptr;
		Node* right = nullptr;
	};

	void propagate(Node* node);

	Node* rightRotate(Node* y);

	Node* leftRotate(Node* x);

	Node* insert(Node* node, int k, int pos, Node* val);

	Node* erase(Node* node, int pos);

	Node* split(int pos);

	void merge(Node* node);

	void getDataFromNodes(Node* node, std::vector<DataBlock>& data);

	Node* m_root = nullptr;
};

#endif
