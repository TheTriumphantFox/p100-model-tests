#include "queen_attack.h"
#include <cmath>
#include <cstdlib>

namespace queen_attack {

chess_board::chess_board(std::pair<int, int> white, std::pair<int, int> black)
    : white_(white), black_(black) {
    // Validate positions are on the board
    if (white_.first < 0 || white_.first > 7 || white_.second < 0 || white_.second > 7) {
        throw std::domain_error("White queen out of bounds");
    }
    if (black_.first < 0 || black_.first > 7 || black_.second < 0 || black_.second > 7) {
        throw std::domain_error("Black queen out of bounds");
    }
    // Validate queens are not on the same square
    if (white_ == black_) {
        throw std::domain_error("Queens on same square");
    }
}

bool chess_board::can_attack() const {
    int row_diff = std::abs(white_.first - black_.first);
    int col_diff = std::abs(white_.second - black_.second);

    // Same row
    if (row_diff == 0) return true;
    // Same column
    if (col_diff == 0) return true;
    // Same diagonal
    if (row_diff == col_diff) return true;

    return false;
}

std::pair<int, int> chess_board::white() const {
    return white_;
}

std::pair<int, int> chess_board::black() const {
    return black_;
}

}  // namespace queen_attack
