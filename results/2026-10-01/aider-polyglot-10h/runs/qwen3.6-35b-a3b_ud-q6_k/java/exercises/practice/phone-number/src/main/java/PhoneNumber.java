class PhoneNumber {

    private final String number;

    PhoneNumber(String numberString) {
        StringBuilder digits = new StringBuilder();
        for (char c : numberString.toCharArray()) {
            if (Character.isDigit(c)) {
                digits.append(c);
            } else if (Character.isLetter(c)) {
                throw new IllegalArgumentException("letters not permitted");
            } else if (c != ' ' && c != '-' && c != '.' && c != '(' && c != ')' && c != '+' && c != '\t' && c != ',') {
                throw new IllegalArgumentException("punctuations not permitted");
            }
        }

        String cleaned = digits.toString();

        if (cleaned.length() < 10) {
            throw new IllegalArgumentException("must not be fewer than 10 digits");
        }
        if (cleaned.length() > 11) {
            throw new IllegalArgumentException("must not be greater than 11 digits");
        }
        if (cleaned.length() == 11) {
            if (!cleaned.startsWith("1")) {
                throw new IllegalArgumentException("11 digits must start with 1");
            }
            cleaned = cleaned.substring(1);
        }

        if (cleaned.charAt(0) == '0') {
            throw new IllegalArgumentException("area code cannot start with zero");
        }
        if (cleaned.charAt(0) == '1') {
            throw new IllegalArgumentException("area code cannot start with one");
        }
        if (cleaned.charAt(3) == '0') {
            throw new IllegalArgumentException("exchange code cannot start with zero");
        }
        if (cleaned.charAt(3) == '1') {
            throw new IllegalArgumentException("exchange code cannot start with one");
        }

        this.number = cleaned;
    }

    String getNumber() {
        return number;
    }

}
