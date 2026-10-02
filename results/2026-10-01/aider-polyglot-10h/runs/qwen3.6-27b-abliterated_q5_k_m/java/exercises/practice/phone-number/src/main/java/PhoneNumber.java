class PhoneNumber {

    private final String number;

    PhoneNumber(String numberString) {
        // Remove all non-digit characters
        String cleaned = numberString.replaceAll("\\D", "");

        // Check for valid length
        if (cleaned.length() == 11) {
            // Check for valid country code
            if (cleaned.startsWith("1")) {
                cleaned = cleaned.substring(1);
            } else {
                throw new IllegalArgumentException("11 digits must start with 1");
            }
        }

        if (cleaned.length() != 10) {
            throw new IllegalArgumentException("must be 10 or 11 digits");
        }

        // Check area code (first digit)
        if (cleaned.charAt(0) < '2' || cleaned.charAt(0) > '9') {
            throw new IllegalArgumentException("area code must start with 2-9");
        }

        // Check exchange code (fourth digit)
        if (cleaned.charAt(3) < '2' || cleaned.charAt(3) > '9') {
            throw new IllegalArgumentException("exchange code must start with 2-9");
        }

        this.number = cleaned;
    }

    String getNumber() {
        return number;
    }

}
