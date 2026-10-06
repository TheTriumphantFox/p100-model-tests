#include "queen_attack.h"

namespace queen_attack {

chess_board::chess_board(std::pair<int, int> white, std::pair<int, int> black)
    : white_(white), black_(black) {
    if (!is_valid()) {
        throw std::domain_error("Invalid queen position");
    }
}

std::pair<int, int> chess_board::white() const {
    return white_;
}

std::pair<int, int> chess_board::black() const {
    return black_;
}

bool chess_board::is_valid() const {
    auto valid_pos = [](std::pair<int, int> p) {
        return p.first >= 0 && p.first <= 7 && p.second >= 0 && p.second <= 7;
    };
    return valid_pos(white_) && valid_pos(black_) && !(white_ == black_);
}

bool chess_board::is_occupied(std::pair<int, int> pos) const {
    return pos == white_ || pos == black_;
}

bool chess_board::can_attack() const {
    int dx = std::abs(white_.first - black_.first);
    int dy = std::abs(white_.second - black_.second);
    return dx == 0 || dy == 0 || dx == dy;
}

queen::queen(std::pair<int, int> pos) : pos_(pos) {
    if (!is_valid()) {
        throw std::domain_error("Invalid queen position");
    }
}

std::pair<int, int> queen::position() const {
    return pos_;
}

bool queen::is_valid() const {
    return pos_.first >= 0 && pos_.first <= 7 && pos_.second >= 0 && pos_.second <= 7;
}

}  // namespace queen_attack
