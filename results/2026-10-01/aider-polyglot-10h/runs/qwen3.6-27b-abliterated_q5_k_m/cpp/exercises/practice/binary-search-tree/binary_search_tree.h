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
        T data() const { return data_; }
        std::shared_ptr<binary_tree<T>> left() const { return left_; }
        std::shared_ptr<binary_tree<T>> right() const { return right_; }

        void insert(T val) {
            insert_helper(this, val);
        }

        // Iterator support for in-order traversal
        class iterator {
        public:
            using difference_type = std::ptrdiff_t;
            using value_type = T;
            using pointer = T*;
            using reference = T&;
            using iterator_category = std::input_iterator_tag;

            iterator() : current_(nullptr), stack_() {}

            iterator(std::shared_ptr<binary_tree<T>> node) : current_(node), stack_() {
                // Push all left nodes onto the stack
                while (current_) {
                    stack_.push_back(current_);
                    current_ = current_->left_;
                }
            }

            reference operator*() const {
                return stack_.back()->data_;
            }

            pointer operator->() const {
                return &(stack_.back()->data_);
            }

            iterator& operator++() {
                if (stack_.empty()) {
                    return *this;
                }
                current_ = stack_.back()->right_;
                stack_.pop_back();
                while (current_) {
                    stack_.push_back(current_);
                    current_ = current_->left_;
                }
                return *this;
            }

            bool operator==(const iterator& other) const {
                return stack_ == other.stack_;
            }

            bool operator!=(const iterator& other) const {
                return stack_ != other.stack_;
            }

        private:
            std::shared_ptr<binary_tree<T>> current_;
            std::vector<std::shared_ptr<binary_tree<T>>> stack_;
        };

        iterator begin() {
            return iterator(shared_from_this());
        }

        iterator end() {
            return iterator();
        }

    private:
        T data_;
        std::shared_ptr<binary_tree<T>> left_;
        std::shared_ptr<binary_tree<T>> right_;

        binary_tree(T val) : data_(val), left_(nullptr), right_(nullptr) {}

        friend std::unique_ptr<binary_tree<T>> make_tree(const std::vector<T>& data);

        static void insert_helper(std::shared_ptr<binary_tree<T>> current, T val) {
            if (val <= current->data_) {
                if (current->left_) {
                    insert_helper(current->left_, val);
                } else {
                    current->left_ = std::make_shared<binary_tree<T>>(val);
                }
            } else {
                if (current->right_) {
                    insert_helper(current->right_, val);
                } else {
                    current->right_ = std::make_shared<binary_tree<T>>(val);
                }
            }
        }
    };

    template <typename T>
    std::unique_ptr<binary_tree<T>> make_tree(const std::vector<T>& data) {
        if (data.empty()) {
            return nullptr;
        }
        auto root = std::make_unique<binary_tree<T>>(data[0]);
        for (size_t i = 1; i < data.size(); ++i) {
            root->insert(data[i]);
        }
        return root;
    }

}  // namespace binary_search_tree

#endif // BINARY_SEARCH_TREE_H
