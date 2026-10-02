#include "diamond.h"
#include <string>
#include <vector>

namespace diamond {

std::vector<std::string> rows(char letter) {
    std::vector<std::string> result;
    int n = letter - 'A';
    int size = 2 * n + 1;

    for (int i = 0; i <= n; ++i) {
        std::string row(size, ' ');
        char current_char = 'A' + i;
        row[n - i] = current_char;
        row[n + i] = current_char;
        result.push_back(row);
    }

    for (int i = n - 1; i >= 0; --i) {
        result.push_back(result[i]);
    }

    return result;
}

}  // namespace diamond
