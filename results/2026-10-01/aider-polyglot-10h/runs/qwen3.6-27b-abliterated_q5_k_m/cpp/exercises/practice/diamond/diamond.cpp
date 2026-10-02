#include "diamond.h"
#include <string>
#include <vector>

namespace diamond {

std::vector<std::string> rows(char letter) {
    int n = letter - 'A';
    int width = 2 * n + 1;
    std::vector<std::string> result;

    for (int i = 0; i <= n; ++i) {
        std::string row(width, ' ');
        char current_char = 'A' + i;
        row[i] = current_char;
        row[width - 1 - i] = current_char;
        result.push_back(row);
    }

    for (int i = n - 1; i >= 0; --i) {
        result.push_back(result[i]);
    }

    return result;
}

}  // namespace diamond
