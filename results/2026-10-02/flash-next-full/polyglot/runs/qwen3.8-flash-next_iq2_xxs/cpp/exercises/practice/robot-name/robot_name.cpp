#include "robot_name.h"
#include <random>
#include <string>
#include <set>

namespace robot_name {

std::set<std::string> robot::used_names_;

robot::robot() {
    name_ = generate_name();
}

std::string robot::name() const {
    return name_;
}

void robot::reset() {
    name_ = generate_name();
}

std::string robot::generate_name() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 25);
    std::uniform_int_distribution<> dis_digit(0, 9);

    std::string new_name;
    do {
        new_name.clear();
        new_name += static_cast<char>('A' + dis(gen));
        new_name += static_cast<char>('A' + dis(gen));
        new_name += static_cast<char>('0' + dis_digit(gen));
        new_name += static_cast<char>('0' + dis_digit(gen));
        new_name += static_cast<char>('0' + dis_digit(gen));
    } while (used_names_.find(new_name) != used_names_.end());

    used_names_.insert(new_name);
    return new_name;
}

}  // namespace robot_name
