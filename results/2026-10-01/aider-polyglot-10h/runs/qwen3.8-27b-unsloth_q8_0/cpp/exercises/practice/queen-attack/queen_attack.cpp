#include "queen_attack.h"
#include <cstdlib>

namespace queen_attack {

Queen::Queen(int row, int column) : row_(row), column_(column) {
    if (row < 0 || row > 7 || column < 0 || column > 7) {
        throw std::domain_error("invalid position");
    }
}

int Queen::row() const {
    return row_;
}

int Queen::column() const {
    return column_;
}

bool Queen::can_attack(const Queen& other) const {
    if (row_ == other.row_ && column_ == other.column_) {
        return false;
    }
    if (row_ == other.row_ || column_ == other.column_) {
        return true;
    }
    int row_diff = row_ - other.row_;
    int col_diff = column_ - other.column_;
    return std::abs(row_diff) == std::abs(col_diff);
}

bool Queen::operator==(const Queen& other) const {
    return row_ == other.row_ && column_ == other.column_;
}

chess_board::chess_board(std::pair<int, int> white, std::pair<int, int> black)
    : white_(white.first, white.second), black_(black.first, black.second) {
    if (white_ == black_) {
        throw std::domain_error("queens cannot occupy the same position");
    }
}

Queen chess_board::white() const {
    return white_;
}

Queen chess_board::black() const {
    return black_;
}

bool chess_board::can_attack() const {
    return white_.can_attack(black_);
}

}  // namespace queen_attack
