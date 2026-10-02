#ifndef ROBOT_NAME_H
#define ROBOT_NAME_H

#include <string>
#include <unordered_set>
#include <random>
#include <mutex>

namespace robot_name {

class robot {
public:
    // Returns the current name of the robot. If the robot has no name yet,
    // a new random unique name is generated.
    std::string name();

    // Resets the robot to factory settings. The next call to name()
    // will generate a new random unique name.
    void reset();

private:
    // Generates a random name in the format: two uppercase letters followed by three digits.
    static std::string generateRandomName();

    // Keeps track of all names currently in use to guarantee uniqueness.
    static std::unordered_set<std::string> used_names_;
    static std::mutex mutex_; // protects used_names_

    // The current name of this robot instance. Empty string means no name.
    std::string current_name_;
};

}  // namespace robot_name

#endif // ROBOT_NAME_H
