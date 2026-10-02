#include "zebra_puzzle.h"
#include <vector>
#include <string>
#include <algorithm>

namespace zebra_puzzle {

namespace {

const std::vector<std::string> nationalities = {
    "Englishman", "Spaniard", "Ukrainian", "Norwegian", "Japanese"
};
const std::vector<std::string> colors = {
    "Red", "Green", "Ivory", "Yellow", "Blue"
};
const std::vector<std::string> pets = {
    "Dog", "Snail", "Fox", "Horse", "Zebra"
};
const std::vector<std::string> drinks = {
    "Coffee", "Tea", "Milk", "Orange Juice", "Water"
};
const std::vector<std::string> hobbies = {
    "Dancing", "Reading", "Painter", "Football", "Chess"
};

// House index 0 to 4
// Attributes: nationality, color, pet, drink, hobby

bool is_valid(const std::vector<std::string>& nat,
              const std::vector<std::string>& col,
              const std::vector<std::string>& pet,
              const std::vector<std::string>& drk,
              const std::vector<std::string>& hob) {
    // 2. The Englishman lives in the red house.
    for (int i = 0; i < 5; ++i) {
        if (nat[i] == "Englishman" && col[i] != "Red") return false;
        if (col[i] == "Red" && nat[i] != "Englishman") return false;
    }

    // 3. The Spaniard owns the dog.
    for (int i = 0; i < 5; ++i) {
        if (nat[i] == "Spaniard" && pet[i] != "Dog") return false;
        if (pet[i] == "Dog" && nat[i] != "Spaniard") return false;
    }

    // 4. The person in the green house drinks coffee.
    for (int i = 0; i < 5; ++i) {
        if (col[i] == "Green" && drk[i] != "Coffee") return false;
        if (drk[i] == "Coffee" && col[i] != "Green") return false;
    }

    // 5. The Ukrainian drinks tea.
    for (int i = 0; i < 5; ++i) {
        if (nat[i] == "Ukrainian" && drk[i] != "Tea") return false;
        if (drk[i] == "Tea" && nat[i] != "Ukrainian") return false;
    }

    // 6. The green house is immediately to the right of the ivory house.
    // "Right" usually means higher index in these puzzles (House 1 is leftmost).
    // So Ivory at i, Green at i+1.
    for (int i = 0; i < 5; ++i) {
        if (col[i] == "Green") {
            if (i == 0) return false; // Can't be left of Ivory if it's the first house
            if (col[i-1] != "Ivory") return false;
        }
        if (col[i] == "Ivory") {
            if (i == 4) return false; // Can't have Green to the right if it's the last house
            if (col[i+1] != "Green") return false;
        }
    }

    // 7. The snail owner likes to go dancing.
    for (int i = 0; i < 5; ++i) {
        if (pet[i] == "Snail" && hob[i] != "Dancing") return false;
        if (hob[i] == "Dancing" && pet[i] != "Snail") return false;
    }

    // 8. The person in the yellow house is a painter.
    for (int i = 0; i < 5; ++i) {
        if (col[i] == "Yellow" && hob[i] != "Painter") return false;
        if (hob[i] == "Painter" && col[i] != "Yellow") return false;
    }

    // 9. The person in the middle house drinks milk.
    if (drk[2] != "Milk") return false;

    // 10. The Norwegian lives in the first house.
    if (nat[0] != "Norwegian") return false;

    // 11. The person who enjoys reading lives in the house next to the person with the fox.
    for (int i = 0; i < 5; ++i) {
        if (hob[i] == "Reading") {
            bool found_fox = false;
            if (i > 0 && pet[i-1] == "Fox") found_fox = true;
            if (i < 4 && pet[i+1] == "Fox") found_fox = true;
            if (!found_fox) return false;
        }
        if (pet[i] == "Fox") {
            bool found_reading = false;
            if (i > 0 && hob[i-1] == "Reading") found_reading = true;
            if (i < 4 && hob[i+1] == "Reading") found_reading = true;
            if (!found_reading) return false;
        }
    }

    // 12. The painter's house is next to the house with the horse.
    for (int i = 0; i < 5; ++i) {
        if (hob[i] == "Painter") {
            bool found_horse = false;
            if (i > 0 && pet[i-1] == "Horse") found_horse = true;
            if (i < 4 && pet[i+1] == "Horse") found_horse = true;
            if (!found_horse) return false;
        }
        if (pet[i] == "Horse") {
            bool found_painter = false;
            if (i > 0 && hob[i-1] == "Painter") found_painter = true;
            if (i < 4 && hob[i+1] == "Painter") found_painter = true;
            if (!found_painter) return false;
        }
    }

    // 13. The person who plays football drinks orange juice.
    for (int i = 0; i < 5; ++i) {
        if (hob[i] == "Football" && drk[i] != "Orange Juice") return false;
        if (drk[i] == "Orange Juice" && hob[i] != "Football") return false;
    }

    // 14. The Japanese person plays chess.
    for (int i = 0; i < 5; ++i) {
        if (nat[i] == "Japanese" && hob[i] != "Chess") return false;
        if (hob[i] == "Chess" && nat[i] != "Japanese") return false;
    }

    // 15. The Norwegian lives next to the blue house.
    // Norwegian is at 0, so Blue must be at 1.
    if (col[1] != "Blue") return false;

    return true;
}

bool solve_recursive(int house,
                     std::vector<std::string>& nat,
                     std::vector<std::string>& col,
                     std::vector<std::string>& pet,
                     std::vector<std::string>& drk,
                     std::vector<std::string>& hob) {
    if (house == 5) {
        return is_valid(nat, col, pet, drk, hob);
    }

    for (const auto& n : nationalities) {
        if (std::find(nat.begin(), nat.end(), n) != nat.end()) continue;
        nat[house] = n;

        for (const auto& c : colors) {
            if (std::find(col.begin(), col.end(), c) != col.end()) continue;
            col[house] = c;

            for (const auto& p : pets) {
                if (std::find(pet.begin(), pet.end(), p) != pet.end()) continue;
                pet[house] = p;

                for (const auto& d : drinks) {
                    if (std::find(drk.begin(), drk.end(), d) != drk.end()) continue;
                    drk[house] = d;

                    for (const auto& h : hobbies) {
                        if (std::find(hob.begin(), hob.end(), h) != hob.end()) continue;
                        hob[house] = h;

                        if (solve_recursive(house + 1, nat, col, pet, drk, hob)) {
                            return true;
                        }
                    }
                }
            }
        }
    }
    return false;
}

} // namespace

Solution solve() {
    std::vector<std::string> nat(5);
    std::vector<std::string> col(5);
    std::vector<std::string> pet(5);
    std::vector<std::string> drk(5);
    std::vector<std::string> hob(5);

    solve_recursive(0, nat, col, pet, drk, hob);

    Solution sol;
    for (int i = 0; i < 5; ++i) {
        if (drk[i] == "Water") {
            sol.drinksWater = nat[i];
        }
        if (pet[i] == "Zebra") {
            sol.ownsZebra = nat[i];
        }
    }
    return sol;
}

}  // namespace zebra_puzzle
