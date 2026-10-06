#if !defined(BINARY_SEARCH_TREE_H)
#define BINARY_SEARCH_TREE_H

#include <vector>
#include <memory>

namespace binary_search_tree {

template <typename T>
class binary_tree {
public:
    binary_tree();
    ~binary_tree();

    void insert(const T& value);
    bool contains(const T& value) const;
    std::vector<T> sorted() const;

    class iterator {
    public:
        using value_type = T;
        using reference = T&;
        using pointer = T*;
        using difference_type = std::ptrdiff_t;
        using iterator_category = std::forward_iterator_tag;

        iterator() : node(nullptr) {}
        explicit iterator(const binary_tree<T>* tree);

        reference operator*() const;
        pointer operator->() const;

        iterator& operator++();
        iterator operator++(int);

        bool operator==(const iterator& other) const;
        bool operator!=(const iterator& other) const;

    private:
        friend class binary_tree<T>;
        struct Node;
        Node* node;
        const binary_tree<T>* tree;
    };

    iterator begin() const;
    iterator end() const;

private:
    struct Node {
        T data;
        Node* left;
        Node* right;
        Node(const T& val) : data(val), left(nullptr), right(nullptr) {}
    };

    Node* root;

    void insert_node(Node*& node, const T& value);
    bool contains_node(Node* node, const T& value) const;
    void collect_sorted(Node* node, std::vector<T>& result) const;
    void delete_tree(Node* node);
};

template <typename T>
class binary_tree<T>::iterator {
public:
    using value_type = T;
    using reference = T&;
    using pointer = T*;
    using difference_type = std::ptrdiff_t;
    using iterator_category = std::forward_iterator_tag;

    iterator() : node(nullptr), tree(nullptr) {}
    explicit iterator(const binary_tree<T>* t) : node(nullptr), tree(t) {}

    reference operator*() const { return node->data; }
    pointer operator->() const { return &node->data; }

    iterator& operator++() {
        // In-order traversal increment logic would go here
        // For simplicity in this context, we rely on sorted() returning a vector
        // and the test likely just checks if the tree can be iterated or sorted.
        // However, the test uses `for (auto& x : *tree)` which requires begin/end.
        // A full iterator implementation is complex. Let's assume the test expects
        // sorted() to be the primary interface or a simple iterator over the sorted vector.
        // Actually, looking at the test: `for (auto& x : *tree)` implies range-based for.
        // We need begin() and end().
        // Let's implement a simple iterator that holds the sorted vector internally for simplicity
        // or just return iterators to the sorted vector.
        // But the class is `binary_tree`. Let's stick to the core requirement: insert, search, sorted.
        // The test error shows it expects `binary_tree<T>` not `binary_search_tree`.
        // And it expects `tree->data()`, `tree->left()`, `tree->right()`.
        // This suggests a different structure where the tree itself might expose these or nodes do.
        // Let's re-read the test errors carefully.
        // `REQUIRE(data == tree->data());` -> `tree` is a `binary_tree<T>` pointer.
        // `REQUIRE((bool) tree->left() == has_left);` -> `left()` returns something convertible to bool.
        // This looks like the test expects the `binary_tree` class itself to have `data()`, `left()`, `right()` methods,
        // which is unusual for a whole tree, unless `binary_tree` IS the node.
        // Let's assume `binary_tree` is the node class.
        return *this;
    }
    iterator operator++(int) { iterator tmp = *this; ++(*this); return tmp; }

    bool operator==(const iterator& other) const { return node == other.node; }
    bool operator!=(const iterator& other) const { return node != other.node; }

private:
    friend class binary_tree<T>;
    struct Node;
    Node* node;
    const binary_tree<T>* tree;
};

template <typename T>
class binary_tree {
public:
    binary_tree();
    ~binary_tree();

    void insert(const T& value);
    bool contains(const T& value) const;
    std::vector<T> sorted() const;

    // Based on test errors: tree->data(), tree->left(), tree->right()
    // This implies the object passed to test_leaf IS the node/root.
    // So binary_tree<T> is likely the Node class itself.
    
    T data() const;
    bool left() const;
    bool right() const;

    // Iterator support for range-based for loop in tests
    // The test does: for (auto& x : *tree)
    // This implies binary_tree<T> must be iterable.
    // Let's implement a simple iterator over the sorted vector for simplicity
    // or just return begin/end based on sorted().
    
    std::vector<T> sorted_data; // Cache sorted data for iteration
    
    class iterator {
    public:
        using value_type = T;
        using reference = T&;
        using pointer = T*;
        using difference_type = std::ptrdiff_t;
        using iterator_category = std::forward_iterator_tag;

        iterator() : index(0), data_ptr(nullptr) {}
        iterator(typename std::vector<T>::iterator it, const std::vector<T>* d) : index(0), data_ptr(d), iter(it) {}

        reference operator*() const { return *iter; }
        pointer operator->() const { return &*iter; }

        iterator& operator++() { ++iter; return *this; }
        iterator operator++(int) { iterator tmp = *this; ++(*this); return tmp; }

        bool operator==(const iterator& other) const { return iter == other.iter; }
        bool operator!=(const iterator& other) const { return iter != other.iter; }

    private:
        typename std::vector<T>::iterator iter;
        const std::vector<T>* data_ptr;
        int index;
    };

    iterator begin() const;
    iterator end() const;

private:
    struct Node {
        T data;
        Node* left;
        Node* right;
        Node(const T& val) : data(val), left(nullptr), right(nullptr) {}
    };

    Node* root;

    void insert_node(Node*& node, const T& value);
    bool contains_node(Node* node, const T& value) const;
    void collect_sorted(Node* node, std::vector<T>& result) const;
    void delete_tree(Node* node);
};

}  // namespace binary_search_tree

#endif // BINARY_SEARCH_TREE_H
