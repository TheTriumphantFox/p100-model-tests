class BowlingGame {

    private final int[] rolls = new int[21];
    private int currentRoll = 0;

    void roll(int pins) {
        if (pins < 0 || pins > 10) {
            throw new IllegalStateException("Invalid pin count: " + pins);
        }
        if (currentRoll >= rolls.length) {
            throw new IllegalStateException("No more rolls allowed");
        }
        // Validate that a frame does not exceed 10 pins (except in the 10th frame with bonus rolls)
        if (!isLastFrameBonusRoll()) {
            if (currentRoll % 2 == 1 && rolls[currentRoll - 1] + pins > 10) {
                throw new IllegalStateException("Frame cannot exceed 10 pins");
            }
        }
        rolls[currentRoll++] = pins;
    }

    int score() {
        if (framesCount() < 10) {
            throw new IllegalStateException("Game is incomplete");
        }
        int score = 0;
        int rollIndex = 0;
        for (int frame = 0; frame < 10; frame++) {
            if (isStrike(rollIndex)) { // strike
                score += 10 + strikeBonus(rollIndex);
                rollIndex += 1;
            } else if (isSpare(rollIndex)) { // spare
                score += 10 + spareBonus(rollIndex);
                rollIndex += 2;
            } else { // open frame
                score += sumOfBallsInFrame(rollIndex);
                rollIndex += 2;
            }
        }
        return score;
    }

    private int framesCount() {
        int frames = 0;
        int rollIndex = 0;
        while (frames < 10 && rollIndex < currentRoll) {
            if (isStrike(rollIndex)) {
                rollIndex += 1;
            } else {
                rollIndex += 2;
            }
            frames++;
        }
        return frames;
    }

    private boolean isLastFrameBonusRoll() {
        // In the 10th frame, after a strike or spare, up to two bonus rolls are allowed.
        // We consider a roll to be a bonus roll if we are already in the 10th frame
        // and the current roll index is beyond the normal 20 rolls.
        return currentRoll >= 20;
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

    private int sumOfBallsInFrame(int rollIndex) {
        return rolls[rollIndex] + rolls[rollIndex + 1];
    }
}
