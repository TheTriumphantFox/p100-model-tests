#include "robot_name.h"

#include <random>
#include <algorithm>

namespace robot_name {

std::set<std::string> Robot::used_names_;

Robot::Robot() {
    name_ = generate_name();
}

std::string const& Robot::name() const {
    return name_;
}

void Robot::reset() {
    name_ = generate_name();
}

std::string Robot::generate_name() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<> dis(0, 25);
    static std::uniform_int_distribution<> num_dis(0, 9);

    std::string new_name;
    do {
        new_name = std::string(2, 'A');
        new_name[0] = 'A' + dis(gen);
        new_name[1] = 'A' + dis(gen);
        for (int i = 0; i < 3; ++i) {
            new_name += '0' + num_dis(gen);
        }
    } while (used_names_.count(new_name));

    used_names_.insert(new_name);
    return new_name;
}

}  // namespace robot_name
