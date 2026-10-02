#include "diamond.h"
#include <vector>
#include <algorithm>

namespace diamond {

std::string rows(char letter) {
    if (letter < 'A' || letter > 'Z') {
        return "";
    }

    std::vector<std::string> diamond;
    int size = letter - 'A' + 1;

    // Build the top half including the middle line
    for (int i = 0; i <= size; ++i) {
        char current_char = 'A' + i;
        int spaces = size - i - 1;
        int char_pos = spaces;

        std::string line(size * 2 - 1, ' ');

        if (i > 0) {
            line[char_pos] = current_char;
            line[size * 2 - 2 - char_pos] = current_char;
        } else {
            line[spaces] = current_char;
        }

        diamond.push_back(line);
    }

    // Build the bottom half (excluding the middle line which we already added)
    for (int i = size - 1; i >= 0; --i) {
        if (i == size) continue; // Skip the middle line we already added
        char current_char = 'A' + i;
        int spaces = size - i - 1;
        int char_pos = spaces;

        std::string line(size * 2 - 1, ' ');

        if (i > 0) {
            line[char_pos] = current_char;
            line[size * 2 - 2 - char_pos] = current_char;
        } else {
            line[spaces] = current_char;
        }

        diamond.push_back(line);
    }

    // Join all lines with newlines
    std::string result;
    for (const auto& line : diamond) {
        result += line + "\n";
    }

    // Remove the trailing newline
    if (!result.empty()) {
        result.pop_back();
    }

    return result;
}

}  // namespace diamond
