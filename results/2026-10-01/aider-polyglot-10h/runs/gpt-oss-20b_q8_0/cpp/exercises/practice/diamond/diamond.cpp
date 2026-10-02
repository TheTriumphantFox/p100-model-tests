#include "diamond.h"

#include <algorithm>
#include <cctype>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace diamond {

static std::string repeat_char(char c, std::size_t n) {
    return std::string(n, c);
}

std::string make_diamond(char letter) {
    if (!std::isupper(static_cast<unsigned char>(letter))) {
        throw std::invalid_argument("letter must be an uppercase ASCII letter");
    }

    const int max_index = letter - 'A';          // 0 for 'A', 2 for 'C', etc.
    const int width = max_index * 2 + 1;         // total width of the diamond

    std::ostringstream oss;

    // Build the upper half including the middle line
    for (int i = 0; i <= max_index; ++i) {
        char current = 'A' + i;
        int leading_spaces = max_index - i;
        oss << repeat_char(' ', leading_spaces);

        if (i == 0) {
            // The top line contains a single 'A'
            oss << current;
        } else {
            // Two identical letters with a space between
            oss << current << ' ' << current;
        }

        oss << repeat_char(' ', leading_spaces);
        if (i != max_index) oss << '\n';
    }

    // Build the lower half (excluding the middle line)
    for (int i = max_index - 1; i >= 0; --i) {
        char current = 'A' + i;
        int leading_spaces = max_index - i;
        oss << repeat_char(' ', leading_spaces);

        if (i == 0) {
            oss << current;
        } else {
            oss << current << ' ' << current;
        }

        oss << repeat_char(' ', leading_spaces);
        if (i != 0) oss << '\n';
    }

    return oss.str();
}

std::vector<std::string> rows(char letter) {
    std::string diamond_str = make_diamond(letter);
    std::vector<std::string> result;
    std::istringstream iss(diamond_str);
    std::string line;
    while (std::getline(iss, line)) {
        result.push_back(line);
    }
    return result;
}

}  // namespace diamond
