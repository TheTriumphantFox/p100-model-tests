#include "zebra_puzzle.h"
#include <algorithm>
#include <vector>
#include <string>

namespace zebra_puzzle {

namespace {

// Helper to check if two indices are adjacent
bool adjacent(int i, int j) {
    return std::abs(i - j) == 1;
}

} // namespace

Solution solve() {
    // We will represent the houses as indices 0 to 4.
    // We need to assign attributes to each house.
    // Attributes: Nationality, Color, Hobby, Beverage, Pet
    
    // Let's fix some positions based on direct clues to reduce search space:
    // Clue 10: Norwegian lives in the first house (index 0).
    // Clue 9: Person in the middle house (index 2) drinks milk.
    
    // We will generate permutations for the remaining attributes.
    // Nationalities: Englishman, Spaniard, Ukrainian, Japanese, Norwegian
    // Colors: Red, Green, Ivory, Yellow, Blue
    // Hobbies: Dancing, Painter, Reading, Football, Chess
    // Beverages: Coffee, Tea, OrangeJuice, Water, Milk
    // Pets: Dog, Snail, Fox, Horse, Zebra
    
    // Since Norwegian is at 0, we permute the other 4 nationalities for indices 1-4.
    // Since Milk is at 2, we permute the other 4 beverages for indices 0,1,3,4.
    
    // To simplify, let's just permute all 5 for each category and check constraints.
    // 5! = 120. 120^5 is too big (24 billion).
    // But we can prune heavily.
    
    // Let's define the domains
    std::vector<std::string> nationalities = {"Englishman", "Spaniard", "Ukrainian", "Japanese", "Norwegian"};
    std::vector<std::string> colors = {"Red", "Green", "Ivory", "Yellow", "Blue"};
    std::vector<std::string> hobbies = {"Dancing", "Painter", "Reading", "Football", "Chess"};
    std::vector<std::string> beverages = {"Coffee", "Tea", "OrangeJuice", "Water", "Milk"};
    std::vector<std::string> pets = {"Dog", "Snail", "Fox", "Horse", "Zebra"};
    
    // We will iterate through permutations.
    // To optimize, we can fix Norwegian at index 0 and Milk at index 2.
    
    // Let's create index vectors for permutation
    std::vector<int> nat_idx = {0, 1, 2, 3, 4};
    std::vector<int> col_idx = {0, 1, 2, 3, 4};
    std::vector<int> hob_idx = {0, 1, 2, 3, 4};
    std::vector<int> bev_idx = {0, 1, 2, 3, 4};
    std::vector<int> pet_idx = {0, 1, 2, 3, 4};
    
    // Fix Norwegian at house 0
    // nat_idx[0] should correspond to "Norwegian" which is index 4 in nationalities vector
    // So we can just permute indices 1-4 for nationalities, keeping 0 fixed to 4?
    // Or simpler: just permute all and check if nat_idx[0] == 4 (Norwegian)
    
    // Fix Milk at house 2
    // bev_idx[2] should correspond to "Milk" which is index 4 in beverages vector
    
    Solution solution;
    
    // Iterate Nationalities
    std::sort(nat_idx.begin(), nat_idx.end());
    do {
        // Clue 10: Norwegian lives in the first house.
        // nationalities[4] is "Norwegian"
        if (nationalities[nat_idx[0]] != "Norwegian") continue;
        
        // Iterate Colors
        std::sort(col_idx.begin(), col_idx.end());
        do {
            // Clue 15: The Norwegian lives next to the blue house.
            // Norwegian is at 0, so Blue must be at 1.
            // colors[4] is "Blue"
            if (colors[col_idx[1]] != "Blue") continue;
            
            // Clue 6: The green house is immediately to the right of the ivory house.
            // Find indices of Green and Ivory
            int green_idx = -1, ivory_idx = -1;
            for (int i = 0; i < 5; ++i) {
                if (colors[col_idx[i]] == "Green") green_idx = i;
                if (colors[col_idx[i]] == "Ivory") ivory_idx = i;
            }
            if (green_idx != ivory_idx + 1) continue;
            
            // Clue 2: The Englishman lives in the red house.
            // Find index of Englishman and Red
            int eng_idx = -1, red_idx = -1;
            for (int i = 0; i < 5; ++i) {
                if (nationalities[nat_idx[i]] == "Englishman") eng_idx = i;
                if (colors[col_idx[i]] == "Red") red_idx = i;
            }
            if (eng_idx != red_idx) continue;
            
            // Iterate Beverages
            std::sort(bev_idx.begin(), bev_idx.end());
            do {
                // Clue 9: The person in the middle house drinks milk.
                // beverages[4] is "Milk"
                if (beverages[bev_idx[2]] != "Milk") continue;
                
                // Clue 4: The person in the green house drinks coffee.
                // beverages[0] is "Coffee"
                if (beverages[bev_idx[green_idx]] != "Coffee") continue;
                
                // Clue 5: The Ukrainian drinks tea.
                // beverages[1] is "Tea"
                int ukr_idx = -1;
                for (int i = 0; i < 5; ++i) {
                    if (nationalities[nat_idx[i]] == "Ukrainian") ukr_idx = i;
                }
                if (beverages[bev_idx[ukr_idx]] != "Tea") continue;
                
                // Clue 13: The person who plays football drinks orange juice.
                // beverages[2] is "OrangeJuice"
                // We need to check hobbies later, but we can note that the house with Football has OrangeJuice.
                
                // Iterate Hobbies
                std::sort(hob_idx.begin(), hob_idx.end());
                do {
                    // Clue 8: The person in the yellow house is a painter.
                    // hobbies[1] is "Painter"
                    int yellow_idx = -1;
                    for (int i = 0; i < 5; ++i) {
                        if (colors[col_idx[i]] == "Yellow") yellow_idx = i;
                    }
                    if (hobbies[hob_idx[yellow_idx]] != "Painter") continue;
                    
                    // Clue 14: The Japanese person plays chess.
                    // hobbies[4] is "Chess"
                    int jap_idx = -1;
                    for (int i = 0; i < 5; ++i) {
                        if (nationalities[nat_idx[i]] == "Japanese") jap_idx = i;
                    }
                    if (hobbies[hob_idx[jap_idx]] != "Chess") continue;
                    
                    // Clue 13: The person who plays football drinks orange juice.
                    // hobbies[3] is "Football"
                    int foot_idx = -1;
                    for (int i = 0; i < 5; ++i) {
                        if (hobbies[hob_idx[i]] == "Football") foot_idx = i;
                    }
                    if (beverages[bev_idx[foot_idx]] != "OrangeJuice") continue;
                    
                    // Iterate Pets
                    std::sort(pet_idx.begin(), pet_idx.end());
                    do {
                        // Clue 3: The Spaniard owns the dog.
                        // pets[0] is "Dog"
                        int span_idx = -1;
                        for (int i = 0; i < 5; ++i) {
                            if (nationalities[nat_idx[i]] == "Spaniard") span_idx = i;
                        }
                        if (pets[pet_idx[span_idx]] != "Dog") continue;
                        
                        // Clue 7: The snail owner likes to go dancing.
                        // pets[1] is "Snail", hobbies[0] is "Dancing"
                        int snail_idx = -1, dance_idx = -1;
                        for (int i = 0; i < 5; ++i) {
                            if (pets[pet_idx[i]] == "Snail") snail_idx = i;
                            if (hobbies[hob_idx[i]] == "Dancing") dance_idx = i;
                        }
                        if (snail_idx != dance_idx) continue;
                        
                        // Clue 11: The person who enjoys reading lives in the house next to the person with the fox.
                        // hobbies[2] is "Reading", pets[2] is "Fox"
                        int read_idx = -1, fox_idx = -1;
                        for (int i = 0; i < 5; ++i) {
                            if (hobbies[hob_idx[i]] == "Reading") read_idx = i;
                            if (pets[pet_idx[i]] == "Fox") fox_idx = i;
                        }
                        if (!adjacent(read_idx, fox_idx)) continue;
                        
                        // Clue 12: The painter's house is next to the house with the horse.
                        // hobbies[1] is "Painter", pets[3] is "Horse"
                        int paint_idx = -1, horse_idx = -1;
                        for (int i = 0; i < 5; ++i) {
                            if (hobbies[hob_idx[i]] == "Painter") paint_idx = i;
                            if (pets[pet_idx[i]] == "Horse") horse_idx = i;
                        }
                        if (!adjacent(paint_idx, horse_idx)) continue;
                        
                        // If we reach here, we have a solution!
                        
                        // Find who drinks water
                        for (int i = 0; i < 5; ++i) {
                            if (beverages[bev_idx[i]] == "Water") {
                                solution.drinksWater = nationalities[nat_idx[i]];
                                break;
                            }
                        }
                        
                        // Find who owns zebra
                        for (int i = 0; i < 5; ++i) {
                            if (pets[pet_idx[i]] == "Zebra") {
                                solution.ownsZebra = nationalities[nat_idx[i]];
                                break;
                            }
                        }
                        
                        return solution;
                        
                    } while (std::next_permutation(pet_idx.begin(), pet_idx.end()));
                    
                } while (std::next_permutation(hob_idx.begin(), hob_idx.end()));
                
            } while (std::next_permutation(bev_idx.begin(), bev_idx.end()));
            
        } while (std::next_permutation(col_idx.begin(), col_idx.end()));
        
    } while (std::next_permutation(nat_idx.begin(), nat_idx.end()));
    
    return solution;
}

}  // namespace zebra_puzzle
