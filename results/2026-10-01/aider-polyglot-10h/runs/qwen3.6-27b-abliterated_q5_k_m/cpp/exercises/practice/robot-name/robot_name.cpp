#include "robot_name.h"
#include <set>
#include <random>
#include <algorithm>
#include <string>

namespace robot_name {

namespace {
    std::set<std::string> used_names;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> letter_dist(0, 25);
    std::uniform_int_distribution<> digit_dist(0, 9);

    std::string generate_unique_name() {
        while (true) {
            std::string new_name;
            new_name += static_cast<char>('A' + letter_dist(gen));
            new_name += static_cast<char>('A' + letter_dist(gen));
            new_name += static_cast<char>('0' + digit_dist(gen));
            new_name += static_cast<char>('0' + digit_dist(gen));
            new_name += static_cast<char>('0' + digit_dist(gen));

            if (used_names.find(new_name) == used_names.end()) {
                used_names.insert(new_name);
                return new_name;
            }
        }
    }
}

robot::robot() : _name(generate_unique_name()) {}

std::string robot::name() const {
    return _name;
}

void robot::reset() {
    _name = generate_unique_name();
}

}  // namespace robot_name
