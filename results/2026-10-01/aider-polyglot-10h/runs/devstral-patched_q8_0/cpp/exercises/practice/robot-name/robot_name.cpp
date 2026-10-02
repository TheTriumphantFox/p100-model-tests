#include "robot_name.h"
#include <random>
#include <ctime>

namespace robot_name {

std::unordered_set<std::string> robot::used_names;

robot::robot() {
    generate_name();
}

std::string robot::name() {
    return name;
}

void robot::reset() {
    used_names.erase(name);
    name.clear();
    generate_name();
}

void robot::generate_name() {
    const std::string letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const std::string digits = "0123456789";

    std::mt19937 rng(static_cast<unsigned int>(std::time(nullptr)));

    std::string new_name;
    do {
        // Generate 2 random letters
        std::uniform_int_distribution<int> letter_dist(0, letters.size() - 1);
        new_name += letters[letter_dist(rng)];
        new_name += letters[letter_dist(rng)];

        // Generate 3 random digits
        std::uniform_int_distribution<int> digit_dist(0, digits.size() - 1);
        new_name += digits[digit_dist(rng)];
        new_name += digits[digit_dist(rng)];
        new_name += digits[digit_dist(rng)];

    } while (used_names.find(new_name) != used_names.end());

    name = new_name;
    used_names.insert(new_name);
}

}  // namespace robot_name
