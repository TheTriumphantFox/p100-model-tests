#include "robot_name.h"

namespace robot_name {

// Static member definitions
std::unordered_set<std::string> robot::used_names_;
std::mutex robot::mutex_;

std::string robot::generateRandomName() {
    static const std::string letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<> letter_dist(0, 25);
    static std::uniform_int_distribution<> digit_dist(0, 9);

    std::string name;
    name.reserve(5);
    // Two uppercase letters
    name += letters[letter_dist(gen)];
    name += letters[letter_dist(gen)];
    // Three digits
    name += std::to_string(digit_dist(gen));
    name += std::to_string(digit_dist(gen));
    name += std::to_string(digit_dist(gen));

    return name;
}

std::string robot::name() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!current_name_.empty()) {
        return current_name_;
    }

    // Generate a unique name
    std::string new_name;
    do {
        new_name = generateRandomName();
    } while (used_names_.find(new_name) != used_names_.end());

    used_names_.insert(new_name);
    current_name_ = new_name;
    return current_name_;
}

void robot::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!current_name_.empty()) {
        used_names_.erase(current_name_);
        current_name_.clear();
    }
}

}  // namespace robot_name
