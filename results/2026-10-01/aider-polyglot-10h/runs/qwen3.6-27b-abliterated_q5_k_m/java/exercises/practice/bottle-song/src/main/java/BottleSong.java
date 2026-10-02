class BottleSong {

    String recite(int startBottles, int takeDown) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < takeDown; i++) {
            sb.append(verse(startBottles - i));
            sb.append("\n");
            if (i < takeDown - 1) {
                sb.append("\n");
            }
        }
        return sb.toString();
    }

    private String verse(int bottles) {
        String currentBottles = numberToWord(bottles);
        String nextBottles = numberToWord(bottles - 1);
        String currentBottleNoun = bottles == 1 ? "bottle" : "bottles";
        String nextBottleNoun = (bottles - 1) == 1 ? "bottle" : "bottles";

        return String.format(
            "%s green %s hanging on the wall,%n" +
            "%s green %s hanging on the wall,%n" +
            "And if one green bottle should accidentally fall,%n" +
            "There'll be %s green %s hanging on the wall.",
            currentBottles, currentBottleNoun,
            currentBottles, currentBottleNoun,
            nextBottles.toLowerCase(), nextBottleNoun
        );
    }

    private String numberToWord(int number) {
        switch (number) {
            case 0: return "no";
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
            default: return String.valueOf(number);
        }
    }

}
