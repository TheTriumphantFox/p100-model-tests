#if !defined(BINARY_SEARCH_TREE_H)
#define BINARY_SEARCH_TREE_H

#include <string>
#include <memory>
#include <vector>
#include <iterator>

namespace binary_search_tree {

template <typename T>
class binary_tree {
public:
    binary_tree(const T& data) : data_(data), left_(nullptr), right_(nullptr) {}

    const T& data() const { return data_; }
    std::unique_ptr<binary_tree<T>> left() const { return std::move(left_); }
    std::unique_ptr<binary_tree<T>> right() const { return std::move(right_); }

    void insert(const T& data) {
        if (data <= this->data_) {
            if (left_) {
                left_->insert(data);
            } else {
                left_ = std::make_unique<binary_tree<T>>(data);
            }
        } else {
            if (right_) {
                right_->insert(data);
            } else {
                right_ = std::make_unique<binary_tree<T>>(data);
            }
        }
    }

    std::vector<T> sorted_data() const {
        std::vector<T> result;
        in_order_traversal(result);
        return result;
    }

private:
    T data_;
    std::unique_ptr<binary_tree<T>> left_;
    std::unique_ptr<binary_tree<T>> right_;

    void in_order_traversal(std::vector<T>& result) const {
        if (left_) {
            left_->in_order_traversal(result);
        }
        result.push_back(data_);
        if (right_) {
            right_->in_order_traversal(result);
        }
    }
};

}  // namespace binary_search_tree

#endif // BINARY_SEARCH_TREE_H
