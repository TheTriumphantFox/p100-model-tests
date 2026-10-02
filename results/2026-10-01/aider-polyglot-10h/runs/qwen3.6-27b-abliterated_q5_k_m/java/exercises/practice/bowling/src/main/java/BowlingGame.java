class BowlingGame {
    private final int[] rolls = new int[21]; // Max possible rolls in a game
    private int currentRoll = 0;
    private int frame = 0;
    private int firstRollPins = 0;
    private boolean gameFinished = false;

    void roll(int pins) {
        if (pins < 0) {
            throw new IllegalStateException("Negative pins");
        }
        if (pins > 10) {
            throw new IllegalStateException("More than 10 pins");
        }

        if (gameFinished) {
            throw new IllegalStateException("Game already finished");
        }

        if (frame < 9) {
            if (currentRoll % 2 == 0) {
                // First roll of a frame
                if (pins == 10) {
                    // Strike
                    rolls[currentRoll++] = pins;
                    frame++;
                } else {
                    // Not a strike, store first roll
                    rolls[currentRoll++] = pins;
                    firstRollPins = pins;
                }
            } else {
                // Second roll of a frame
                if (firstRollPins + pins > 10) {
                    throw new IllegalStateException("Two rolls in a frame can not score more than 10 points");
                }
                rolls[currentRoll++] = pins;
                frame++;
                firstRollPins = 0;
            }
        } else {
            // 10th frame logic
            if (currentRoll == 18) {
                // First roll of 10th frame
                if (pins == 10) {
                    // Strike, need two more rolls
                    rolls[currentRoll++] = pins;
                    firstRollPins = 10;
                } else {
                    rolls[currentRoll++] = pins;
                    firstRollPins = pins;
                }
            } else if (currentRoll == 19) {
                // Second roll of 10th frame
                if (firstRollPins == 10) {
                    // First roll was a strike, second roll can be anything 0-10
                    if (pins > 10) {
                        throw new IllegalStateException("Bonus roll after a strike in the last frame can not score more than 10 points");
                    }
                    rolls[currentRoll++] = pins;
                    if (pins == 10) {
                        // Second roll is also a strike, need one more roll
                        firstRollPins = 10;
                    } else {
                        firstRollPins = pins;
                    }
                } else {
                    // First roll was not a strike
                    if (firstRollPins + pins > 10) {
                        throw new IllegalStateException("Two rolls in a frame can not score more than 10 points");
                    }
                    rolls[currentRoll++] = pins;
                    if (firstRollPins + pins == 10) {
                        // Spare, need one more roll
                        firstRollPins = 10; // Mark as needing one more roll
                    } else {
                        // Open frame, game over
                        gameFinished = true;
                    }
                }
            } else if (currentRoll == 20) {
                // Third roll of 10th frame (bonus roll)
                if (firstRollPins == 10) {
                    // Previous two rolls were strikes, this roll can be 0-10
                    if (pins > 10) {
                        throw new IllegalStateException("Second bonus roll after a strike in the last frame can not score more than 10 points");
                    }
                    rolls[currentRoll++] = pins;
                    gameFinished = true;
                } else {
                    // Previous rolls resulted in a spare, this roll can be 0-10
                    if (pins > 10) {
                        throw new IllegalStateException("Bonus roll for a spare in the last frame can not score more than 10 points");
                    }
                    rolls[currentRoll++] = pins;
                    gameFinished = true;
                }
            } else {
                // Should not reach here if logic is correct
                throw new IllegalStateException("Too many rolls");
            }
        }
    }

    int score() {
        if (frame < 9) {
            throw new IllegalStateException("Game not finished");
        }
        if (frame == 9 && !gameFinished) {
            // Check if 10th frame is complete
            if (currentRoll < 19) {
                throw new IllegalStateException("Game not finished");
            }
            // If 10th frame started with a strike, we need 3 rolls total for the frame
            if (rolls[18] == 10 && currentRoll < 21) {
                // Check if we have enough rolls
                if (currentRoll == 19) {
                     throw new IllegalStateException("Game not finished");
                }
                // If second roll was not a strike, we need 3 rolls total
                if (rolls[18] == 10 && rolls[19] != 10 && currentRoll < 21) {
                     throw new IllegalStateException("Game not finished");
                }
            }
            // If 10th frame started with a spare, we need 3 rolls total for the frame
            if (rolls[18] + rolls[19] == 10 && rolls[18] != 10 && currentRoll < 21) {
                 throw new IllegalStateException("Game not finished");
            }
        }

        int score = 0;
        int frameIndex = 0;

        for (int f = 0; f < 10; f++) {
            if (isStrike(frameIndex)) {
                // Strike: 10 + next two rolls
                score += 10 + rolls[frameIndex + 1] + rolls[frameIndex + 2];
                frameIndex += 1;
            } else if (isSpare(frameIndex)) {
                // Spare: 10 + next roll
                score += 10 + rolls[frameIndex + 2];
                frameIndex += 2;
            } else {
                // Open frame: sum of two rolls
                score += rolls[frameIndex] + rolls[frameIndex + 1];
                frameIndex += 2;
            }
        }
        return score;
    }

    private boolean isStrike(int frameIndex) {
        return rolls[frameIndex] == 10;
    }

    private boolean isSpare(int frameIndex) {
        return rolls[frameIndex] + rolls[frameIndex + 1] == 10;
    }
}
