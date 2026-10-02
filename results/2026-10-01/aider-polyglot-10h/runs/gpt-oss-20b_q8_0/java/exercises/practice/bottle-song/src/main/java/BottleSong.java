class BottleSong {

    private static final String[] NUMBER_WORDS = {
        "no", "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine", "ten"
    };

    String recite(int startBottles, int takeDown) {
        StringBuilder sb = new StringBuilder();
        for (int i = startBottles; i > startBottles - takeDown; i--) {
            int next = i - 1;
            String currentBottle = i == 1 ? "bottle" : "bottles";
            String nextBottle = next == 1 ? "bottle" : "bottles";
            String currentCount = NUMBER_WORDS[i];
            String nextCount = NUMBER_WORDS[next];

            sb.append(currentCount).append(" green ").append(currentBottle)
              .append(" hanging on the wall,\n");
            sb.append(currentCount).append(" green ").append(currentBottle)
              .append(" hanging on the wall,\n");
            sb.append("And if one green bottle should accidentally fall,\n");
            sb.append("There'll be ").append(nextCount).append(" green ")
              .append(nextBottle).append(" hanging on the wall.\n");

            if (i > startBottles - takeDown) {
                sb.append("\n");
            }
        }
        // Remove the trailing newline if present
        if (sb.length() > 0 && sb.charAt(sb.length() - 1) == '\n') {
            sb.setLength(sb.length() - 1);
        }
        return sb.toString();
    }

}
