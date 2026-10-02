#if !defined(ROBOT_NAME_H)
#define ROBOT_NAME_H

#include <string>
#include <set>

namespace robot_name {

class Robot {
public:
    Robot();
    std::string const& name() const;
    void reset();

private:
    std::string generate_name();
    std::string name_;
    static std::set<std::string> used_names_;
};

using robot = Robot;

}  // namespace robot_name

#endif // ROBOT_NAME_H
