#if !defined(QUEEN_ATTACK_H)
#define QUEEN_ATTACK_H

#include <utility>
#include <stdexcept>
#include <cmath>
#include <cstdlib>

namespace queen_attack {

class chess_board {
public:
    chess_board(std::pair<int, int> white, std::pair<int, int> black)
        : white_(white), black_(black) {
        if (!valid_position(white_) || !valid_position(black_)) {
            throw std::domain_error("Invalid position");
        }
        if (white_ == black_) {
            throw std::domain_error("Queens cannot occupy the same square");
        }
    }

    std::pair<int, int> white() const {
        return white_;
    }

    std::pair<int, int> black() const {
        return black_;
    }

    bool can_attack() const {
        int dy = std::abs(black_.first - white_.first);
        int dx = std::abs(black_.second - white_.second);
        return dy == 0 || dx == 0 || dy == dx;
    }

private:
    std::pair<int, int> white_;
    std::pair<int, int> black_;

    bool valid_position(std::pair<int, int> pos) const {
        return pos.first >= 0 && pos.first < 8 && pos.second >= 0 && pos.second < 8;
    }
};

}  // namespace queen_attack

#endif // QUEEN_ATTACK_H
