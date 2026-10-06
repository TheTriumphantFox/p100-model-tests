class BottleSong {

    String recite(int startBottles, int takeDown) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < takeDown; i++) {
            int current = startBottles - i;
            int next = current - 1;
            
            String currentWord = numberToWord(current);
            String nextWord = numberToWordLower(next);
            String currentBottle = current == 1 ? "bottle" : "bottles";
            String nextBottle = next == 1 ? "bottle" : "bottles";

            sb.append(currentWord).append(" green ").append(currentBottle).append(" hanging on the wall,\n");
            sb.append(currentWord).append(" green ").append(currentBottle).append(" hanging on the wall,\n");
            sb.append("And if one green bottle should accidentally fall,\n");
            sb.append("There'll be ").append(nextWord).append(" green ").append(nextBottle).append(" hanging on the wall.");

            if (i < takeDown - 1) {
                sb.append("\n\n");
            }
        }
        return sb.toString();
    }

    private String numberToWord(int n) {
        switch (n) {
            case 1: return "One";
            case 2: return "Two";
            case 3: return "Three";
            case 4: return "Four";
            case 5: return "Five";
            case 6: return "Six";
            case 7: return "Seven";
            case 8: return "Eight";
            case 9: return "Nine";
            case 10: return "Ten";
            default: return String.valueOf(n);
        }
    }

    private String numberToWordLower(int n) {
        switch (n) {
            case 0: return "no";
            case 1: return "one";
            case 2: return "two";
            case 3: return "three";
            case 4: return "four";
            case 5: return "five";
            case 6: return "six";
            case 7: return "seven";
            case 8: return "eight";
            case 9: return "nine";
            case 10: return "ten";
            default: return String.valueOf(n);
        }
    }

}
