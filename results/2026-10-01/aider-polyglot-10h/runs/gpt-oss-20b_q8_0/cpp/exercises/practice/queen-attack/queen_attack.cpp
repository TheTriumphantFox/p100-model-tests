#include "queen_attack.h"
#include <cmath>

namespace queen_attack {

bool can_attack(int w_col, int w_row, int b_col, int b_row) {
    // Same column
    if (w_col == b_col) return true;
    // Same row
    if (w_row == b_row) return true;
    // Same diagonal: difference in columns equals difference in rows
    if (std::abs(w_col - b_col) == std::abs(w_row - b_row)) return true;
    return false;
}

chess_board::chess_board(std::pair<int,int> white, std::pair<int,int> black)
    : white_(white), black_(black)
{
    auto is_valid = [](int col, int row) {
        return col >= 0 && col < 8 && row >= 0 && row < 8;
    };
    if (!is_valid(white_.first, white_.second) ||
        !is_valid(black_.first, black_.second) ||
        (white_ == black_)) {
        throw std::domain_error("Invalid queen positions");
    }
}

bool chess_board::can_attack() const {
    return can_attack(white_.first, white_.second,
                      black_.first, black_.second);
}

}  // namespace queen_attack
