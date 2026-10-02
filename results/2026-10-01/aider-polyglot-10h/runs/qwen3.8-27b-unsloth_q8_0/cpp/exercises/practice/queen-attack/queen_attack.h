#if !defined(QUEEN_ATTACK_H)
#define QUEEN_ATTACK_H

#include <stdexcept>
#include <utility>

namespace queen_attack {

class Queen {
public:
    explicit Queen(int row, int column);
    int row() const;
    int column() const;
    bool can_attack(const Queen& other) const;
    bool operator==(const Queen& other) const;

private:
    int row_;
    int column_;
};

class chess_board {
public:
    chess_board(std::pair<int, int> white, std::pair<int, int> black);
    Queen white() const;
    Queen black() const;
    bool can_attack() const;

private:
    Queen white_;
    Queen black_;
};

}  // namespace queen_attack

#endif // QUEEN_ATTACK_H
