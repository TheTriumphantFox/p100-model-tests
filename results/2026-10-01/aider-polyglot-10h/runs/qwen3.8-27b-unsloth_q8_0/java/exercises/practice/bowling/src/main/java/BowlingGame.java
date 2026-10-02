import java.util.ArrayList;
import java.util.List;

class BowlingGame {

    private final List<Integer> rolls = new ArrayList<>();

    void roll(int pins) {
        if (pins < 0 || pins > 10) {
            throw new IllegalArgumentException("Pin count must be between 0 and 10");
        }

        if (isGameOver()) {
            throw new IllegalStateException("Cannot roll after game is over");
        }

        int frameNumber = getCurrentFrameNumber();
        int rollInFrame = getRollInFrame();

        if (frameNumber < 10) {
            if (rollInFrame == 1) {
                int firstRoll = rolls.get(rolls.size() - 1);
                if (firstRoll + pins > 10) {
                    throw new IllegalArgumentException("Pin count exceeds 10 in frame");
                }
            }
        } else {
            // Frame 10 logic
            if (rollInFrame == 1) {
                // First roll of 10th frame
            } else if (rollInFrame == 2) {
                int firstRoll = rolls.get(rolls.size() - 1);
                if (firstRoll < 10) {
                    // If first roll was not a strike, second roll cannot exceed remaining pins
                    if (firstRoll + pins > 10) {
                        throw new IllegalArgumentException("Pin count exceeds 10 in frame");
                    }
                }
            } else if (rollInFrame == 3) {
                // Third roll is only possible if first was strike or first two were spare
                int firstRoll = rolls.get(rolls.size() - 2);
                int secondRoll = rolls.get(rolls.size() - 1);
                
                if (firstRoll == 10) {
                    // First was strike, second and third are independent bonus rolls
                    // No sum constraint between second and third if first was strike
                } else {
                    // First was not strike, so second must have made a spare (first+second==10)
                    // Third roll is independent
                }
            }
        }

        rolls.add(pins);
    }

    int score() {
        if (!isGameOver()) {
            throw new IllegalStateException("Cannot score before game is over");
        }

        int score = 0;
        int rollIndex = 0;

        for (int frame = 0; frame < 10; frame++) {
            if (frame < 9) {
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
            } else {
                // 10th frame: just sum the remaining rolls
                while (rollIndex < rolls.size()) {
                    score += rolls.get(rollIndex);
                    rollIndex++;
                }
            }
        }

        return score;
    }

    private boolean isGameOver() {
        if (rolls.size() < 2) {
            return false;
        }

        int frameNumber = getCurrentFrameNumber();
        if (frameNumber < 10) {
            return false;
        }

        // Check if 10th frame is complete
        int rollInFrame = getRollInFrame();
        if (rollInFrame == 0) {
            return false;
        }

        // We are in frame 10
        // Find the start index of frame 10
        int index = 0;
        for (int i = 0; i < 9; i++) {
            if (rolls.get(index) == 10) {
                index += 1;
            } else {
                index += 2;
            }
        }
        
        int firstRoll = rolls.get(index);
        int secondRoll = rolls.size() > index + 1 ? rolls.get(index + 1) : 0;
        int thirdRoll = rolls.size() > index + 2 ? rolls.get(index + 2) : 0;

        if (firstRoll == 10) {
            // Strike in 10th frame: needs 2 more rolls
            return rolls.size() >= index + 3;
        } else if (firstRoll + secondRoll == 10) {
            // Spare in 10th frame: needs 1 more roll
            return rolls.size() >= index + 3;
        } else {
            // Open frame in 10th: game over after 2 rolls
            return rolls.size() >= index + 2;
        }
    }

    private int getCurrentFrameNumber() {
        int frame = 1;
        int index = 0;
        while (index < rolls.size() && frame <= 10) {
            if (frame < 10) {
                if (rolls.get(index) == 10) {
                    index += 1;
                } else {
                    index += 2;
                }
            } else {
                // In 10th frame, we just stop counting frames
                break;
            }
            frame++;
        }
        return frame;
    }

    private int getRollInFrame() {
        int frame = 1;
        int index = 0;
        while (index < rolls.size() && frame < 10) {
            if (rolls.get(index) == 10) {
                index += 1;
            } else {
                index += 2;
            }
            frame++;
        }
        
        if (frame < 10) {
            // Not in 10th frame yet
            // Determine if we are on 1st or 2nd roll of current frame
            // If the last roll was a strike, we are on 1st roll of next frame (which is current)
            // Actually, simpler: look at the last roll added.
            // If we just added a roll, and it wasn't a strike (in frames 1-9), it's the 2nd roll.
            // If it was a strike, it's the 1st roll.
            // But we need to know the state *before* adding the new roll to validate it?
            // No, roll() is called, then we add.
            // So inside roll(), before adding, we check the state.
            
            // Let's re-evaluate getRollInFrame usage.
            // It is used in roll() to determine validation rules.
            // At the start of roll(), rolls contains all previous rolls.
            
            if (rolls.isEmpty()) {
                return 0; // 1st roll of 1st frame
            }
            
            int lastRoll = rolls.get(rolls.size() - 1);
            if (lastRoll == 10) {
                return 0; // Next roll is 1st of new frame
            } else {
                return 1; // Next roll is 2nd of current frame
            }
        } else {
            // In 10th frame
            // Count rolls in 10th frame
            int count = 0;
            // We need to find where 10th frame starts
            int idx = 0;
            for (int i = 0; i < 9; i++) {
                if (rolls.get(idx) == 10) {
                    idx += 1;
                } else {
                    idx += 2;
                }
            }
            count = rolls.size() - idx;
            return count;
        }
    }
}
