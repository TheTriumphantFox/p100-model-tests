#include "queen_attack.h"
#include <stdexcept>

namespace queen_attack {

    chess_board::chess_board(std::pair<int, int> white, std::pair<int, int> black) {
        // Validate positions are on the board (0-7 for both row and column)
        auto validate_position = [](const std::pair<int, int>& pos) {
            if (pos.first < 0 || pos.first > 7 || pos.second < 0 || pos.second > 7) {
                throw std::domain_error("Queen position must be between 0 and 7 for both row and column");
            }
        };

        validate_position(white);
        validate_position(black);

        // Check that queens are not on the same position
        if (white == black) {
            throw std::domain_error("Queens cannot occupy the same position");
        }

        white_queen = white;
        black_queen = black;
    }

    std::pair<int, int> chess_board::white() const {
        return white_queen;
    }

    std::pair<int, int> chess_board::black() const {
        return black_queen;
    }

    bool chess_board::can_attack() const {
        int white_row = white_queen.first;
        int white_col = white_queen.second;
        int black_row = black_queen.first;
        int black_col = black_queen.second;

        // Check if queens are on the same row, column, or diagonal
        return (white_row == black_row) ||
               (white_col == black_col) ||
               (abs(white_row - black_row) == abs(white_col - black_col));
    }

}  // namespace queen_attack
