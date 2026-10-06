import java.util.Objects;

class Rational {

    private final int numerator;
    private final int denominator;

    Rational(int numerator, int denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("Denominator cannot be zero");
        }
        
        // Reduce to lowest terms
        int gcd = gcd(Math.abs(numerator), Math.abs(denominator));
        int newNum = numerator / gcd;
        int newDen = denominator / gcd;

        // Ensure standard form (denominator positive)
        if (newDen < 0) {
            newNum = -newNum;
            newDen = -newDen;
        }

        this.numerator = newNum;
        this.denominator = newDen;
    }

    private static int gcd(int a, int b) {
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    int getNumerator() {
        return numerator;
    }

    int getDenominator() {
        return denominator;
    }

    Rational add(Rational other) {
        int newNumerator = this.numerator * other.denominator + other.numerator * this.denominator;
        int newDenominator = this.denominator * other.denominator;
        return new Rational(newNumerator, newDenominator);
    }

    Rational subtract(Rational other) {
        int newNumerator = this.numerator * other.denominator - other.numerator * this.denominator;
        int newDenominator = this.denominator * other.denominator;
        return new Rational(newNumerator, newDenominator);
    }

    Rational multiply(Rational other) {
        int newNumerator = this.numerator * other.numerator;
        int newDenominator = this.denominator * other.denominator;
        return new Rational(newNumerator, newDenominator);
    }

    Rational divide(Rational other) {
        int newNumerator = this.numerator * other.denominator;
        int newDenominator = this.denominator * other.numerator;
        return new Rational(newNumerator, newDenominator);
    }

    Rational abs() {
        return new Rational(Math.abs(this.numerator), Math.abs(this.denominator));
    }

    Rational pow(int power) {
        if (power == 0) {
            return new Rational(1, 1);
        }
        
        int newNumerator = (int) Math.pow(this.numerator, Math.abs(power));
        int newDenominator = (int) Math.pow(this.denominator, Math.abs(power));

        if (power < 0) {
            // Swap numerator and denominator for negative power
            return new Rational(newDenominator, newNumerator);
        } else {
            return new Rational(newNumerator, newDenominator);
        }
    }

    double exp(double exponent) {
        return Math.pow(exponent, (double) this.numerator / this.denominator);
    }

    @Override
    public String toString() {
        return String.format("%d/%d", this.getNumerator(), this.getDenominator());
    }

    @Override
    public boolean equals(Object obj) {
        if (obj instanceof Rational other) {
            return this.getNumerator() == other.getNumerator()
                    && this.getDenominator() == other.getDenominator();
        }

        return false;
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.getNumerator(), this.getDenominator());
    }
}
