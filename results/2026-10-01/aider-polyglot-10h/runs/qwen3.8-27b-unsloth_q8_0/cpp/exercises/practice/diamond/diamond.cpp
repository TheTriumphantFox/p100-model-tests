#include "diamond.h"
#include <stdexcept>

namespace diamond {

std::vector<std::string> rows(const char letter) {
    if (letter < 'A' || letter > 'Z') {
        throw std::invalid_argument("Input must be an uppercase letter");
    }
    
    int n = letter - 'A';
    int size = 2 * n + 1;
    std::vector<std::string> result;
    
    for (int row = 0; row < size; ++row) {
        // Determine which letter to use for this row
        int letter_idx;
        if (row <= n) {
            letter_idx = row;
        } else {
            letter_idx = size - 1 - row;
        }
        
        char current_letter = 'A' + letter_idx;
        std::string line(size, ' ');
        
        if (letter_idx == 0) {
            // Only 'A' appears once in the middle
            line[n] = 'A';
        } else {
            // Other letters appear twice
            int left_pos = n - letter_idx;
            int right_pos = n + letter_idx;
            line[left_pos] = current_letter;
            line[right_pos] = current_letter;
        }
        
        result.push_back(line);
    }
    
    return result;
}

}  // namespace diamond
