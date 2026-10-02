#pragma once

#include <string>
#include <vector>

namespace diamond {

/// Generates a diamond string for the given uppercase letter.
/// The returned string contains newline characters (`'\n'`) separating rows.
/// Example for letter 'C':
/// ```text
///   A
///  B B
/// C   C
///  B B
///   A
/// ```
/// The function assumes `letter` is an uppercase ASCII letter between 'A' and 'Z'.
std::string make_diamond(char letter);

/// Returns the diamond as a vector of rows (each row is a string).
/// This helper is used by the unit tests to compare individual lines.
std::vector<std::string> rows(char letter);

}  // namespace diamond
