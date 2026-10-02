class BowlingGame {
    private int[] rolls = new int[21];
    private int currentRoll = 0;
    private int currentFrame = 0;

    void roll(int pins) {
        if (pins < 0 || pins > 10) {
            throw new IllegalStateException("Roll must be between 0 and 10");
        }

        if (currentFrame >= 10) {
            throw new IllegalStateException("Cannot roll after game is complete");
        }

        if (isLastFrame()) {
            handleLastFrameRoll(pins);
        } else {
            handleRegularFrameRoll(pins);
        }

        rolls[currentRoll++] = pins;
    }

    int score() {
        if (currentFrame < 10) {
            throw new IllegalStateException("Game is not complete");
        }

        int score = 0;
        int rollIndex = 0;

        for (int frame = 0; frame < 10; frame++) {
            if (isStrike(rollIndex)) {
                score += 10 + strikeBonus(rollIndex);
                rollIndex += 1;
            } else if (isSpare(rollIndex)) {
                score += 10 + spareBonus(rollIndex);
                rollIndex += 2;
            } else {
                score += sumOfBallInFrame(rollIndex);
                rollIndex += 2;
            }
        }
        return score;
    }

    private boolean isLastFrame() {
        return currentFrame == 9;
    }

    private void handleRegularFrameRoll(int pins) {
        if (isStrike(currentRoll)) {
            currentFrame++;
        } else if (currentRoll % 2 == 1 && rolls[currentRoll] + pins > 10) {
            throw new IllegalStateException("Two rolls in a frame cannot score more than 10 points");
        } else if (currentRoll % 2 == 1) {
            // First roll of frame - no special handling needed
        } else {
            currentFrame++;
        }
    }

    private void handleLastFrameRoll(int pins) {
        if (currentRoll == 18) {
            if (rolls[18] == 10) {
                throw new IllegalStateException("Cannot roll after bonus roll for strike");
            }
        } else if (currentRoll == 19) {
            if (rolls[18] + rolls[19] == 10) {
                throw new IllegalStateException("Cannot roll after bonus roll for spare");
            }
        } else if (currentRoll == 20) {
            throw new IllegalStateException("Cannot roll after bonus rolls for strike");
        }

        if (currentRoll == 18) {
            if (rolls[18] == 10) {
                // First bonus roll after strike - can be anything
            } else if (rolls[18] + pins > 10) {
                throw new IllegalStateException("Two rolls in a frame cannot score more than 10 points");
            }
        } else if (currentRoll == 19) {
            if (rolls[18] == 10 && pins > 10) {
                throw new IllegalStateException("Bonus roll after strike cannot score more than 10 points");
            } else if (rolls[18] + rolls[19] == 10 && pins > 10) {
                throw new IllegalStateException("Bonus roll after spare cannot score more than 10 points");
            } else if (rolls[18] == 10 && rolls[19] != 10 && pins == 10) {
                throw new IllegalStateException("Second bonus roll cannot be a strike if first was not");
            }
        }
    }

    private boolean isStrike(int rollIndex) {
        return rolls[rollIndex] == 10;
    }

    private boolean isSpare(int rollIndex) {
        return rolls[rollIndex] + rolls[rollIndex + 1] == 10;
    }

    private int strikeBonus(int rollIndex) {
        return rolls[rollIndex + 1] + rolls[rollIndex + 2];
    }

    private int spareBonus(int rollIndex) {
        return rolls[rollIndex + 2];
    }

    private int sumOfBallInFrame(int rollIndex) {
        return rolls[rollIndex] + rolls[rollIndex + 1];
    }
}
