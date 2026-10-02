#if !defined(QUEEN_ATTACK_H)
#define QUEEN_ATTACK_H

#include <utility>
#include <stdexcept>

namespace queen_attack {

/// Determine whether two queens can attack each other on an 8x8 chessboard.
/// @param w_col Column of the white queen (0-7).
/// @param w_row Row of the white queen (0-7).
/// @param b_col Column of the black queen (0-7).
/// @param b_row Row of the black queen (0-7).
/// @return true if the queens share the same row, column, or diagonal; false otherwise.
bool can_attack(int w_col, int w_row, int b_col, int b_row);

/// A simple representation of a chess board with two queens.
/// The constructor validates that the positions are on the board and not the same.
/// The method can_attack() reports whether the two queens can attack each other.
class chess_board {
public:
    /// Construct a board with the given queen positions.
    /// @param white Position of the white queen as a pair (col,row).
    /// @param black Position of the black queen as a pair (col,row).
    /// @throws std::domain_error if a position is off the board or both queens share the same square.
    chess_board(std::pair<int,int> white, std::pair<int,int> black);

    /// Return the position of the white queen.
    std::pair<int,int> white() const { return white_; }

    /// Return the position of the black queen.
    std::pair<int,int> black() const { return black_; }

    /// Return true if the two queens can attack each other.
    bool can_attack() const;

private:
    std::pair<int,int> white_;
    std::pair<int,int> black_;
};

}  // namespace queen_attack

#endif // QUEEN_ATTACK_H
