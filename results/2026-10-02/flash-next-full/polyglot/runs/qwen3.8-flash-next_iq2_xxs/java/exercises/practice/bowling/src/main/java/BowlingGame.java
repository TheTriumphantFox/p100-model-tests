class BowlingGame {

    private int[] rolls = new int[21];
    private int currentRoll = 0;
    private int currentFrame = 0;

    void roll(int pins) {
        if (currentFrame >= 10 && isGameOver()) {
            throw new IllegalStateException("Game is over");
        }
        if (pins < 0 || pins > 10) {
            throw new IllegalArgumentException("Pins must be between 0 and 10");
        }
        if (currentFrame < 10) {
            if (currentRoll % 2 == 1) {
                if (rolls[currentRoll - 1] + pins > 10) {
                    throw new IllegalArgumentException("Sum of rolls in a frame cannot exceed 10");
                }
            }
        }
        rolls[currentRoll++] = pins;
        if (currentFrame < 10) {
            if (currentRoll % 2 == 0 || rolls[currentRoll - 1] == 10) {
                currentFrame++;
            }
        }
    }

    int score() {
        if (!isGameOver()) {
            throw new IllegalStateException("Game is not over");
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
                score += sumOfTwoRolls(rollIndex);
                rollIndex += 2;
            }
        }
        return score;
    }

    private boolean isGameOver() {
        if (currentFrame < 10) {
            return false;
        }
        if (currentFrame == 10) {
            if (rolls[currentRoll - 1] == 10) {
                return currentRoll % 2 == 0;
            } else if (currentRoll % 2 == 0 && rolls[currentRoll - 2] + rolls[currentRoll - 1] == 10) {
                return true;
            } else {
                return currentRoll % 2 == 0;
            }
        }
        return true;
    }

    private boolean isStrike(int rollIndex) {
        return rolls[rollIndex] == 10;
    }

    private int strikeBonus(int rollIndex) {
        return rolls[rollIndex + 1] + rolls[rollIndex + 2];
    }

    private boolean isSpare(int rollIndex) {
        return rolls[rollIndex] + rolls[rollIndex + 1] == 10;
    }

    private int spareBonus(int rollIndex) {
        return rolls[rollIndex + 2];
    }

    private int sumOfTwoRolls(int rollIndex) {
        return rolls[rollIndex] + rolls[rollIndex + 1];
    }

}
