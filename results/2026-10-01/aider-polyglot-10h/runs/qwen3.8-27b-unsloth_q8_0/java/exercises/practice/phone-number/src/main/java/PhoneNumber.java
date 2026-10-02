class PhoneNumber {

    private final String number;

    PhoneNumber(String numberString) {
        // Remove all non-digit characters
        String digits = numberString.replaceAll("[^0-9]", "");

        if (digits.length() == 11) {
            if (!digits.startsWith("1")) {
                throw new IllegalArgumentException("11 digits must start with 1");
            }
            digits = digits.substring(1);
        }

        if (digits.length() != 10) {
            throw new IllegalArgumentException("must be 10 digits");
        }

        char firstDigit = digits.charAt(0);
        if (firstDigit == '0') {
            throw new IllegalArgumentException("area code cannot start with 0");
        }
        if (firstDigit == '1') {
            throw new IllegalArgumentException("area code cannot start with 1");
        }

        char fourthDigit = digits.charAt(3);
        if (fourthDigit == '0') {
            throw new IllegalArgumentException("exchange code cannot start with 0");
        }
        if (fourthDigit == '1') {
            throw new IllegalArgumentException("exchange code cannot start with 1");
        }

        this.number = digits;
    }

    String getNumber() {
        return number;
    }

}
