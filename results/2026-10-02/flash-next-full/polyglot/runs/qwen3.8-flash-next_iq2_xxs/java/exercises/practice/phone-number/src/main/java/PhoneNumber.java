class PhoneNumber {

    private String number;

    PhoneNumber(String numberString) {
        // Remove all non-digit characters
        String cleaned = numberString.replaceAll("\\D", "");

        if (cleaned.length() == 11) {
            if (cleaned.charAt(0) != '1') {
                throw new IllegalArgumentException("Invalid country code");
            }
            cleaned = cleaned.substring(1);
        }

        if (cleaned.length() != 10) {
            throw new IllegalArgumentException("Invalid phone number length");
        }

        // Validate area code and exchange code (must be 2-9)
        if (cleaned.charAt(0) < '2' || cleaned.charAt(3) < '2') {
            throw new IllegalArgumentException("Invalid area code or exchange code");
        }

        this.number = cleaned;
    }

    String getNumber() {
        return number;
    }

}
