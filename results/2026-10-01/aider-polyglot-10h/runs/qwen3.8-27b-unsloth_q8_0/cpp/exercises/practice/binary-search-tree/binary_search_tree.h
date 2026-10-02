#if !defined(BINARY_SEARCH_TREE_H)
#define BINARY_SEARCH_TREE_H

namespace binary_search_tree {

class Bst {
public:
    Bst();
    Bst(int data);
    ~Bst();

    // Rule of Five: prevent copying to avoid double-delete issues with raw pointers
    Bst(const Bst&) = delete;
    Bst& operator=(const Bst&) = delete;

    void insert(int data);
    bool contains(int data) const;
    int root() const;
    const Bst& left() const;
    const Bst& right() const;

private:
    int data_;
    Bst* left_;
    Bst* right_;
    bool empty_;
};

}  // namespace binary_search_tree

#endif // BINARY_SEARCH_TREE_H
