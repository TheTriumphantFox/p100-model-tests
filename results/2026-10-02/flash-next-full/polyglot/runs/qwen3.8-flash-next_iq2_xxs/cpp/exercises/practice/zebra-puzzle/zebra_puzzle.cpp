#include "zebra_puzzle.h"
#include <vector>
#include <string>
#include <algorithm>

namespace zebra_puzzle {

namespace {

    const std::vector<std::string> colors = {"red", "green", "ivory", "yellow", "blue"};
    const std::vector<std::string> nationalities = {"Englishman", "Spaniard", "Ukrainian", "Norwegian", "Japanese"};
    const std::vector<std::string> pets = {"dog", "snail", "fox", "horse", "zebra"};
    const std::vector<std::string> drinks = {"coffee", "tea", "milk", "orange juice", "water"};
    const std::vector<std::string> hobbies = {"dancing", "painting", "reading", "football", "chess"};

    bool checkConstraints(const std::vector<int>& color, const std::vector<int>& nationality, const std::vector<int>& pet, const std::vector<int>& drink, const std::vector<int>& hobby) {
        // Helper to get index of item in house array
        auto getHouse = [](const std::vector<std::string>& items, const std::string& item) -> int {
            auto it = std::find(items.begin(), items.end(), item);
            if (it == items.end()) return -1;
            return static_cast<int>(std::distance(items.begin(), it));
        };

        int red = getHouse(colors, "red");
        int green = getHouse(colors, "green");
        int ivory = getHouse(colors, "ivory");
        int yellow = getHouse(colors, "yellow");
        int blue = getHouse(colors, "blue");

        int englishman = getHouse(nationalities, "Englishman");
        int spaniard = getHouse(nationalities, "Spaniard");
        int ukrainian = getHouse(nationalities, "Ukrainian");
        int norwegian = getHouse(nationalities, "Norwegian");
        int japanese = getHouse(nationalities, "Japanese");

        int dog = getHouse(pets, "dog");
        int snail = getHouse(pets, "snail");
        int fox = getHouse(pets, "fox");
        int horse = getHouse(pets, "horse");

        int coffee = getHouse(drinks, "coffee");
        int tea = getHouse(drinks, "tea");
        int milk = getHouse(drinks, "milk");
        int orangeJuice = getHouse(drinks, "orange juice");

        int dancing = getHouse(hobbies, "dancing");
        int painting = getHouse(hobbies, "painting");
        int reading = getHouse(hobbies, "reading");
        int football = getHouse(hobbies, "football");
        int chess = getHouse(hobbies, "chess");

        // 2. The Englishman lives in the red house.
        if (nationality[red] != englishman) return false;
        // 3. The Spaniard owns the dog.
        if (pet[spaniard] != dog) return false;
        // 4. The person in the green house drinks coffee.
        if (drink[green] != coffee) return false;
        // 5. The Ukrainian drinks tea.
        if (drink[ukrainian] != tea) return false;
        // 6. The green house is immediately to the right of the ivory house.
        if (green != ivory + 1) return false;
        // 7. The snail owner likes to go dancing.
        if (hobby[snail] != dancing) return false;
        // 8. The person in the yellow house is a painter.
        if (hobby[yellow] != painting) return false;
        // 9. The person in the middle house drinks milk.
        if (drink[2] != milk) return false;
        // 10. The Norwegian lives in the first house.
        if (nationality[0] != norwegian) return false;
        // 11. The person who enjoys reading lives in the house next to the person with the fox.
        if (!(reading == fox - 1 || reading == fox + 1)) return false;
        // 12. The painter's house is next to the house with the horse.
        if (!(painting == horse - 1 || painting == horse + 1)) return false;
        // 13. The person who plays football drinks orange juice.
        if (drink[football] != orangeJuice) return false;
        // 14. The Japanese person plays chess.
        if (hobby[japanese] != chess) return false;
        // 15. The Norwegian lives next to the blue house.
        if (!(norwegian == blue - 1 || norwegian == blue + 1)) return false;

        return true;
    }

    bool solveRecursive(int house, std::vector<int>& color, std::vector<int>& nationality, std::vector<int>& pet, std::vector<int>& drink, std::vector<int>& hobby) {
        if (house == 5) {
            return checkConstraints(color, nationality, pet, drink, hobby);
        }

        // Try assigning each color to house 'house'
        for (int i = 0; i < 5; ++i) {
            bool used = false;
            for (int j = 0; j < house; ++j) {
                if (color[j] == i) {
                    used = true;
                    break;
                }
            }
            if (used) continue;
            
            color[house] = i;
            
            // Try assigning each nationality to house 'house'
            for (int k = 0; k < 5; ++k) {
                bool usedNat = false;
                for (int j = 0; j < house; ++j) {
                    if (nationality[j] == k) {
                        usedNat = true;
                        break;
                    }
                }
                if (usedNat) continue;
                
                nationality[house] = k;
                
                // Try assigning each pet to house 'house'
                for (int l = 0; l < 5; ++l) {
                    bool usedPet = false;
                    for (int j = 0; j < house; ++j) {
                        if (pet[j] == l) {
                            usedPet = true;
                            break;
                        }
                    }
                    if (usedPet) continue;
                    
                    pet[house] = l;
                    
                    // Try assigning each drink to house 'house'
                    for (int m = 0; m < 5; ++m) {
                        bool usedDrink = false;
                        for (int j = 0; j < house; ++j) {
                            if (drink[j] == m) {
                                usedDrink = true;
                                break;
                            }
                        }
                        if (usedDrink) continue;
                        
                        drink[house] = m;
                        
                        // Try assigning each hobby to house 'house'
                        for (int n = 0; n < 5; ++n) {
                            bool usedHobby = false;
                            for (int j = 0; j < house; ++j) {
                                if (hobby[j] == n) {
                                    usedHobby = true;
                                    break;
                                }
                            }
                            if (usedHobby) continue;
                            
                            hobby[house] = n;
                            
                            if (solveRecursive(house + 1, color, nationality, pet, drink, hobby)) {
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
    std::vector<int> color(5, -1);
    std::vector<int> nationality(5, -1);
    std::vector<int> pet(5, -1);
    std::vector<int> drink(5, -1);
    std::vector<int> hobby(5, -1);

    // Initialize with -1 to indicate unassigned
    for (int i = 0; i < 5; ++i) {
        color[i] = -1;
        nationality[i] = -1;
        pet[i] = -1;
        drink[i] = -1;
        hobby[i] = -1;
    }

    // Start recursive solving from house 0
    solveRecursive(0, color, nationality, pet, drink, hobby);

    // Find who drinks water and who owns zebra
    std::string waterDrinker;
    std::string zebraOwner;

    for (int i = 0; i < 5; ++i) {
        if (drink[i] == 4) { // Index of "water" in drinks vector
            waterDrinker = nationalities[nationality[i]];
        }
        if (pet[i] == 4) { // Index of "zebra" in pets vector
            zebraOwner = nationalities[nationality[i]];
        }
    }

    return {waterDrinker, zebraOwner};
}

}  // namespace zebra_puzzle
