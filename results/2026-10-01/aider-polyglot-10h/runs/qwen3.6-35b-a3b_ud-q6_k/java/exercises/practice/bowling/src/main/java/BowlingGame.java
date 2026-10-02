import java.util.ArrayList;
import java.util.List;

class BowlingGame {

    private final List<Integer> rolls = new ArrayList<>();

    void roll(int pins) {
        if (pins < 0) {
            throw new IllegalStateException("Negative roll is invalid");
        }
        if (pins > 10) {
            throw new IllegalStateException("Pin count exceeds pins on the lane");
        }

        if (isGameFinished()) {
            throw new IllegalStateException("Cannot roll after game is over");
        }

        if (!isGameValidState()) {
             throw new IllegalStateException("Invalid game state");
        }

        rolls.add(pins);
    }

    private boolean isGameValidState() {
        // Check frame constraints
        int rollIndex = 0;
        for (int frame = 0; frame < 10; frame++) {
            if (rollIndex >= rolls.size()) {
                break;
            }
            
            if (rolls.get(rollIndex) == 10) {
                // Strike
                rollIndex++;
            } else {
                if (rollIndex + 1 >= rolls.size()) {
                    break;
                }
                int first = rolls.get(rollIndex);
                int second = rolls.get(rollIndex + 1);
                if (first + second > 10) {
                    return false;
                }
                rollIndex += 2;
            }
        }
        
        // If we are here, basic frame constraints are met.
        // We need to check if we are in a state where a roll is impossible but we haven't finished?
        // Actually, the main validation is usually done by checking if the new roll makes the game invalid.
        // But since we add then check finish, we should check if the current rolls list is valid so far.
        
        // Special check for 10th frame fill balls
        if (rollIndex < rolls.size()) {
             // We are in or past 10th frame
             // Let's re-evaluate 10th frame specifically
             int r = 0;
             for (int f = 0; f < 9; f++) {
                 if (rolls.get(r) == 10) {
                     r++;
                 } else {
                     r += 2;
                 }
             }
             
             // r is now at start of 10th frame
             if (r >= rolls.size()) return true;
             
             int first = rolls.get(r);
             if (first == 10) {
                 // Strike in 10th
                 if (rolls.size() == r + 1) return true; // Only first ball
                 int second = rolls.get(r + 1);
                 if (rolls.size() == r + 2) {
                     // Two balls so far
                     if (second == 10) return true; // Strike, second strike
                     if (first + second > 10) return false; // Should not happen due to earlier check? No, strike is 10.
                     // If first is strike, second can be anything <= 10.
                     return true;
                 }
                 if (rolls.size() == r + 3) {
                     int third = rolls.get(r + 2);
                     // If second was strike, third can be anything <= 10
                     // If second was not strike, sum of second+third <= 10
                     if (second == 10) {
                         return true;
                     } else {
                         return second + third <= 10;
                     }
                 }
             } else {
                 // Not strike in 10th
                 if (rolls.size() == r + 1) return true;
                 int second = rolls.get(r + 1);
                 if (rolls.size() == r + 2) {
                     if (first + second > 10) return false;
                     if (first + second == 10) {
                         // Spare, need one more
                         return true;
                     } else {
                         // Open, game should be finished
                         return true;
                     }
                 }
                 if (rolls.size() == r + 3) {
                     int third = rolls.get(r + 2);
                     if (first + second == 10) {
                         return true;
                     } else {
                         // Should not have 3rd ball if open
                         return false;
                     }
                 }
             }
        }
        
        return true;
    }

    int score() {
        if (!isGameFinished()) {
            throw new IllegalStateException("Score cannot be taken until the end of the game");
        }

        int score = 0;
        int rollIndex = 0;

        for (int frame = 0; frame < 10; frame++) {
            if (rolls.get(rollIndex) == 10) {
                // Strike
                score += 10 + rolls.get(rollIndex + 1) + rolls.get(rollIndex + 2);
                rollIndex += 1;
            } else if (rolls.get(rollIndex) + rolls.get(rollIndex + 1) == 10) {
                // Spare
                score += 10 + rolls.get(rollIndex + 2);
                rollIndex += 2;
            } else {
                // Open frame
                score += rolls.get(rollIndex) + rolls.get(rollIndex + 1);
                rollIndex += 2;
            }
        }

        return score;
    }

    private boolean isGameFinished() {
        if (rolls.isEmpty()) {
            return false;
        }

        int rollIndex = 0;
        int frame = 0;
        
        // Simulate frame progression to see if we've completed 10 frames
        while (frame < 10 && rollIndex < rolls.size()) {
            if (rolls.get(rollIndex) == 10) {
                // Strike
                rollIndex += 1;
            } else {
                if (rollIndex + 1 >= rolls.size()) {
                    return false;
                }
                rollIndex += 2;
            }
            frame++;
        }

        if (frame < 10) {
            return false;
        }

        // Check 10th frame specifics
        // If we are here, we have processed 10 frames logically.
        // We need to ensure enough rolls exist for the 10th frame bonuses if applicable.
        
        // Re-calculate specifically for the 10th frame validation
        int r = 0;
        for (int f = 0; f < 9; f++) {
            if (rolls.get(r) == 10) {
                r += 1;
            } else {
                r += 2;
            }
        }
        
        // Now r points to the start of the 10th frame
        if (r >= rolls.size()) {
            return false;
        }
        
        int firstBall = rolls.get(r);
        if (firstBall == 10) {
            // Strike in 10th frame. Needs 2 more balls.
            return rolls.size() >= r + 3;
        } else {
            if (r + 1 >= rolls.size()) {
                return false;
            }
            int secondBall = rolls.get(r + 1);
            if (firstBall + secondBall == 10) {
                // Spare in 10th frame. Needs 1 more ball.
                return rolls.size() >= r + 3;
            } else {
                // Open frame in 10th. Needs exactly 2 balls.
                return rolls.size() >= r + 2;
            }
        }
    }
}
