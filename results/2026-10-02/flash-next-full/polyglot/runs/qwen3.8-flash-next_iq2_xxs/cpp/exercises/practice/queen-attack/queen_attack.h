#if !defined(QUEEN_ATTACK_H)
#define QUEEN_ATTACK_H

#include <utility>
#include <stdexcept>
#include <cmath>

namespace queen_attack {

class chess_board {
public:
    chess_board(std::pair<int, int> white, std::pair<int, int> black);
    std::pair<int, int> white() const;
    std::pair<int, int> black() const;
    bool is_valid() const;
    bool is_occupied(std::pair<int, int> pos) const;
    bool can_attack() const;

private:
    std::pair<int, int> white_;
    std::pair<int, int> black_;
};

class queen {
public:
    queen(std::pair<int, int> pos);
    std::pair<int, int> position() const;
    bool is_valid() const;

private:
    std::pair<int, int> pos_;
};

}  // namespace queen_attack

#endif // QUEEN_ATTACK_H
