#include "zebra_puzzle.h"
#include <algorithm>
#include <array>
#include <vector>
#include <string>

namespace zebra_puzzle {

namespace {

enum class Nationality { Englishman, Spaniard, Ukrainian, Norwegian, Japanese };
enum class Color { Red, Green, Ivory, Yellow, Blue };
enum class Drink { Coffee, Tea, Milk, OrangeJuice, Water };
enum class Hobby { Dancing, Painter, Reading, Football, Chess };
enum class Pet { Dog, Snail, Fox, Horse, Zebra };

std::string nationality_name(Nationality n) {
    switch (n) {
        case Nationality::Englishman: return "Englishman";
        case Nationality::Spaniard: return "Spaniard";
        case Nationality::Ukrainian: return "Ukrainian";
        case Nationality::Norwegian: return "Norwegian";
        case Nationality::Japanese: return "Japanese";
    }
    return "";
}

struct House {
    Nationality nationality;
    Color color;
    Drink drink;
    Hobby hobby;
    Pet pet;
};

bool solve_recursive(std::array<House, 5>& houses, int index) {
    if (index == 5) {
        // Check all constraints
        // 2. The Englishman lives in the red house.
        bool found = false;
        for (const auto& h : houses) {
            if (h.nationality == Nationality::Englishman && h.color == Color::Red) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 3. The Spaniard owns the dog.
        found = false;
        for (const auto& h : houses) {
            if (h.nationality == Nationality::Spaniard && h.pet == Pet::Dog) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 4. The person in the green house drinks coffee.
        found = false;
        for (const auto& h : houses) {
            if (h.color == Color::Green && h.drink == Drink::Coffee) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 5. The Ukrainian drinks tea.
        found = false;
        for (const auto& h : houses) {
            if (h.nationality == Nationality::Ukrainian && h.drink == Drink::Tea) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 6. The green house is immediately to the right of the ivory house.
        found = false;
        for (int i = 0; i < 4; ++i) {
            if (houses[i].color == Color::Ivory && houses[i+1].color == Color::Green) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 7. The snail owner likes to go dancing.
        found = false;
        for (const auto& h : houses) {
            if (h.pet == Pet::Snail && h.hobby == Hobby::Dancing) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 8. The person in the yellow house is a painter.
        found = false;
        for (const auto& h : houses) {
            if (h.color == Color::Yellow && h.hobby == Hobby::Painter) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 9. The person in the middle house drinks milk.
        if (houses[2].drink != Drink::Milk) return false;

        // 10. The Norwegian lives in the first house.
        if (houses[0].nationality != Nationality::Norwegian) return false;

        // 11. The person who enjoys reading lives in the house next to the person with the fox.
        found = false;
        for (int i = 0; i < 5; ++i) {
            if (houses[i].hobby == Hobby::Reading) {
                if (i > 0 && houses[i-1].pet == Pet::Fox) found = true;
                if (i < 4 && houses[i+1].pet == Pet::Fox) found = true;
                break;
            }
        }
        if (!found) return false;

        // 12. The painter's house is next to the house with the horse.
        found = false;
        for (int i = 0; i < 5; ++i) {
            if (houses[i].hobby == Hobby::Painter) {
                if (i > 0 && houses[i-1].pet == Pet::Horse) found = true;
                if (i < 4 && houses[i+1].pet == Pet::Horse) found = true;
                break;
            }
        }
        if (!found) return false;

        // 13. The person who plays football drinks orange juice.
        found = false;
        for (const auto& h : houses) {
            if (h.hobby == Hobby::Football && h.drink == Drink::OrangeJuice) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 14. The Japanese person plays chess.
        found = false;
        for (const auto& h : houses) {
            if (h.nationality == Nationality::Japanese && h.hobby == Hobby::Chess) {
                found = true;
                break;
            }
        }
        if (!found) return false;

        // 15. The Norwegian lives next to the blue house.
        found = false;
        for (int i = 0; i < 5; ++i) {
            if (houses[i].nationality == Nationality::Norwegian) {
                if (i > 0 && houses[i-1].color == Color::Blue) found = true;
                if (i < 4 && houses[i+1].color == Color::Blue) found = true;
                break;
            }
        }
        if (!found) return false;

        return true;
    }

    // Try all combinations for the current house
    std::array<Nationality, 5> nationalities = {
        Nationality::Englishman, Nationality::Spaniard, Nationality::Ukrainian,
        Nationality::Norwegian, Nationality::Japanese
    };
    std::array<Color, 5> colors = {
        Color::Red, Color::Green, Color::Ivory, Color::Yellow, Color::Blue
    };
    std::array<Drink, 5> drinks = {
        Drink::Coffee, Drink::Tea, Drink::Milk, Drink::OrangeJuice, Drink::Water
    };
    std::array<Hobby, 5> hobbies = {
        Hobby::Dancing, Hobby::Painter, Hobby::Reading, Hobby::Football, Hobby::Chess
    };
    std::array<Pet, 5> pets = {
        Pet::Dog, Pet::Snail, Pet::Fox, Pet::Horse, Pet::Zebra
    };

    for (auto n : nationalities) {
        // Check uniqueness
        bool n_unique = true;
        for (int i = 0; i < index; ++i) {
            if (houses[i].nationality == n) {
                n_unique = false;
                break;
            }
        }
        if (!n_unique) continue;

        for (auto c : colors) {
            bool c_unique = true;
            for (int i = 0; i < index; ++i) {
                if (houses[i].color == c) {
                    c_unique = false;
                    break;
                }
            }
            if (!c_unique) continue;

            for (auto d : drinks) {
                bool d_unique = true;
                for (int i = 0; i < index; ++i) {
                    if (houses[i].drink == d) {
                        d_unique = false;
                        break;
                    }
                }
                if (!d_unique) continue;

                for (auto h : hobbies) {
                    bool h_unique = true;
                    for (int i = 0; i < index; ++i) {
                        if (houses[i].hobby == h) {
                            h_unique = false;
                            break;
                        }
                    }
                    if (!h_unique) continue;

                    for (auto p : pets) {
                        bool p_unique = true;
                        for (int i = 0; i < index; ++i) {
                            if (houses[i].pet == p) {
                                p_unique = false;
                                break;
                            }
                        }
                        if (!p_unique) continue;

                        houses[index] = {n, c, d, h, p};

                        // Early pruning for specific constraints
                        // 10. The Norwegian lives in the first house.
                        if (index == 0 && n != Nationality::Norwegian) continue;

                        // 9. The person in the middle house drinks milk.
                        if (index == 2 && d != Drink::Milk) continue;

                        // 15. The Norwegian lives next to the blue house.
                        if (n == Nationality::Norwegian) {
                            if (index > 0 && houses[index-1].color != Color::Blue) continue;
                            if (index < 4 && houses[index+1].color != Color::Blue) continue;
                        }

                        // 2. The Englishman lives in the red house.
                        if (n == Nationality::Englishman && c != Color::Red) continue;

                        // 4. The person in the green house drinks coffee.
                        if (c == Color::Green && d != Drink::Coffee) continue;

                        // 5. The Ukrainian drinks tea.
                        if (n == Nationality::Ukrainian && d != Drink::Tea) continue;

                        // 8. The person in the yellow house is a painter.
                        if (c == Color::Yellow && h != Hobby::Painter) continue;

                        // 13. The person who plays football drinks orange juice.
                        if (h == Hobby::Football && d != Drink::OrangeJuice) continue;

                        // 14. The Japanese person plays chess.
                        if (n == Nationality::Japanese && h != Hobby::Chess) continue;

                        // 3. The Spaniard owns the dog.
                        if (n == Nationality::Spaniard && p != Pet::Dog) continue;

                        // 7. The snail owner likes to go dancing.
                        if (p == Pet::Snail && h != Hobby::Dancing) continue;

                        // 6. The green house is immediately to the right of the ivory house.
                        if (c == Color::Ivory) {
                            if (index < 4 && houses[index+1].color != Color::Green) continue;
                        }
                        if (c == Color::Green) {
                            if (index > 0 && houses[index-1].color != Color::Ivory) continue;
                        }

                        if (solve_recursive(houses, index + 1)) {
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
    std::array<House, 5> houses;
    solve_recursive(houses, 0);

    Solution sol;
    for (const auto& h : houses) {
        if (h.drink == Drink::Water) {
            sol.drinksWater = nationality_name(h.nationality);
        }
        if (h.pet == Pet::Zebra) {
            sol.ownsZebra = nationality_name(h.nationality);
        }
    }
    return sol;
}

}  // namespace zebra_puzzle
