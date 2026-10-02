import java.util.Objects;

class Rational {

    private final int numerator;
    private final int denominator;

    Rational(int numerator, int denominator) {
        if (denominator == 0) {
            throw new IllegalArgumentException("Denominator cannot be zero");
        }

        int num = numerator;
        int den = denominator;

        // Ensure standard form: denominator is positive
        if (den < 0) {
            num = -num;
            den = -den;
        }

        // Reduce to lowest terms
        int gcd = gcd(Math.abs(num), den);
        if (gcd != 0) {
            num /= gcd;
            den /= gcd;
        }

        this.numerator = num;
        this.denominator = den;
    }

    int getNumerator() {
        return this.numerator;
    }

    int getDenominator() {
        return this.denominator;
    }

    Rational add(Rational other) {
        int num = this.numerator * other.denominator + other.numerator * this.denominator;
        int den = this.denominator * other.denominator;
        return new Rational(num, den);
    }

    Rational subtract(Rational other) {
        int num = this.numerator * other.denominator - other.numerator * this.denominator;
        int den = this.denominator * other.denominator;
        return new Rational(num, den);
    }

    Rational multiply(Rational other) {
        int num = this.numerator * other.numerator;
        int den = this.denominator * other.denominator;
        return new Rational(num, den);
    }

    Rational divide(Rational other) {
        if (other.numerator == 0) {
            throw new ArithmeticException("Division by zero");
        }
        int num = this.numerator * other.denominator;
        int den = this.denominator * other.numerator;
        return new Rational(num, den);
    }

    Rational abs() {
        return new Rational(Math.abs(this.numerator), this.denominator);
    }

    Rational pow(int power) {
        if (power >= 0) {
            int num = 1;
            int den = 1;
            for (int i = 0; i < power; i++) {
                num *= this.numerator;
                den *= this.denominator;
            }
            return new Rational(num, den);
        } else {
            // Negative power: (a/b)^-n = (b/a)^n
            int m = -power;
            int num = 1;
            int den = 1;
            for (int i = 0; i < m; i++) {
                num *= this.denominator;
                den *= this.numerator;
            }
            return new Rational(num, den);
        }
    }

    double exp(double exponent) {
        // x^(a/b) = exp((a/b) * ln(x))
        if (exponent == 0) {
            return 1.0;
        }
        return Math.exp((double) this.numerator / this.denominator * Math.log(exponent));
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

    private static int gcd(int a, int b) {
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }
}
