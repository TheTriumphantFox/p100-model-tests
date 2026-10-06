#include "diamond.h"
#include <string>
#include <vector>

namespace diamond {

std::vector<std::string> rows(char max_letter) {
    std::vector<std::string> result;
    if (max_letter < 'A' || max_letter > 'Z') {
        return result;
    }
    
    int n = max_letter - 'A';
    int width = 2 * n + 1;
    
    for (int i = 0; i <= n; ++i) {
        std::string row(width, ' ');
        char current_char = 'A' + i;
        int center = n;
        int dist = n - i;
        
        row[center - dist] = current_char;
        if (dist > 0) {
            row[center + dist] = current_char;
        }
        
        result.push_back(row);
    }
    
    for (int i = n - 1; i >= 0; --i) {
        std::string row(width, ' ');
        char current_char = 'A' + i;
        int center = n;
        int dist = n - i;
        
        row[center - dist] = current_char;
        if (dist > 0) {
            row[center + dist] = current_char;
        }
        
        result.push_back(row);
    }
    
    return result;
}

}  // namespace diamond
