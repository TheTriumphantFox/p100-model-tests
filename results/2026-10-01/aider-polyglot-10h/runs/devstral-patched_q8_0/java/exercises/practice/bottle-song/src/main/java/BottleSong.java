class BottleSong {

    String recite(int startBottles, int takeDown) {
        StringBuilder result = new StringBuilder();
        int bottles = startBottles;

        for (int i = 0; i < takeDown; i++) {
            if (i > 0) {
                result.append("\n");
            }

            result.append(getVerse(bottles));
            bottles--;
        }

        return result.toString();
    }

    private String getVerse(int bottles) {
        String bottleWord = bottles == 1 ? "bottle" : "bottles";
        String nextBottleWord = bottles - 1 == 1 ? "bottle" : "bottles";
        String bottleCount = convertNumberToWord(bottles);
        String nextBottleCount = convertNumberToWord(bottles - 1);

        return String.format("%s green %s hanging on the wall,\n" +
                             "%s green %s hanging on the wall,\n" +
                             "And if one green bottle should accidentally fall,\n" +
                             "There'll be %s green %s hanging on the wall.",
                             bottleCount, bottleWord, bottleCount, bottleWord, nextBottleCount, nextBottleWord);
    }

    private String convertNumberToWord(int number) {
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
