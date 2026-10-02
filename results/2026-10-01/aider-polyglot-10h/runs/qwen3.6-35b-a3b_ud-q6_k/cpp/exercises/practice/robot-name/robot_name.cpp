#include "robot_name.h"
#include <string>
#include <set>
#include <random>
#include <stdexcept>

namespace robot_name {

namespace {
    std::set<std::string> used_names;
    
    std::string generate_unique_name() {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        
        std::uniform_int_distribution<> letter_dist(0, 25);
        std::uniform_int_distribution<> digit_dist(0, 9);

        while (true) {
            char c1 = 'A' + letter_dist(gen);
            char c2 = 'A' + letter_dist(gen);
            char d1 = '0' + digit_dist(gen);
            char d2 = '0' + digit_dist(gen);
            char d3 = '0' + digit_dist(gen);

            std::string new_name;
            new_name += c1;
            new_name += c2;
            new_name += d1;
            new_name += d2;
            new_name += d3;

            if (used_names.find(new_name) == used_names.end()) {
                used_names.insert(new_name);
                return new_name;
            }
        }
    }
}

robot::robot() : name_() {}

std::string robot::name() const {
    if (name_.empty()) {
        name_ = generate_unique_name();
    }
    return name_;
}

void robot::reset() {
    if (!name_.empty()) {
        used_names.erase(name_);
        name_ = "";
    }
}

}  // namespace robot_name
