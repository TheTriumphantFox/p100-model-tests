#include "binary_search_tree.h"

namespace binary_search_tree {

Bst::Bst() : data_(0), left_(nullptr), right_(nullptr), empty_(true) {}

Bst::Bst(int data) : data_(data), left_(nullptr), right_(nullptr), empty_(false) {}

Bst::~Bst() {
    delete left_;
    delete right_;
}

void Bst::insert(int data) {
    if (empty_) {
        return;
    }

    if (data <= data_) {
        if (left_ == nullptr) {
            left_ = new Bst(data);
        } else {
            left_->insert(data);
        }
    } else {
        if (right_ == nullptr) {
            right_ = new Bst(data);
        } else {
            right_->insert(data);
        }
    }
}

bool Bst::contains(int data) const {
    if (empty_) {
        return false;
    }
    if (data == data_) {
        return true;
    } else if (data < data_) {
        return left_ != nullptr && left_->contains(data);
    } else {
        return right_ != nullptr && right_->contains(data);
    }
}

int Bst::root() const {
    return data_;
}

const Bst& Bst::left() const {
    if (left_ == nullptr) {
        static const Bst empty;
        return empty;
    }
    return *left_;
}

const Bst& Bst::right() const {
    if (right_ == nullptr) {
        static const Bst empty;
        return empty;
    }
    return *right_;
}

}  // namespace binary_search_tree
