import java.util.Objects;

class Rational {

    private final int numerator;
    private final int denominator;

    Rational(int numerator, int denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("Denominator cannot be zero");
        }
        
        int common = gcd(Math.abs(numerator), Math.abs(denominator));
        
        int n = numerator / common;
        int d = denominator / common;
        
        if (d < 0) {
            n = -n;
            d = -d;
        }
        
        this.numerator = n;
        this.denominator = d;
    }

    int getNumerator() {
        return numerator;
    }

    int getDenominator() {
        return denominator;
    }

    Rational add(Rational other) {
        int n = this.numerator * other.denominator + other.numerator * this.denominator;
        int d = this.denominator * other.denominator;
        return new Rational(n, d);
    }

    Rational subtract(Rational other) {
        int n = this.numerator * other.denominator - other.numerator * this.denominator;
        int d = this.denominator * other.denominator;
        return new Rational(n, d);
    }

    Rational multiply(Rational other) {
        int n = this.numerator * other.numerator;
        int d = this.denominator * other.denominator;
        return new Rational(n, d);
    }

    Rational divide(Rational other) {
        if (other.numerator == 0) {
            throw new ArithmeticException("Division by zero");
        }
        int n = this.numerator * other.denominator;
        int d = this.denominator * other.numerator;
        return new Rational(n, d);
    }

    Rational abs() {
        return new Rational(Math.abs(this.numerator), Math.abs(this.denominator));
    }

    Rational pow(int power) {
        if (power < 0) {
            return new Rational((int) Math.pow(this.denominator, -power), (int) Math.pow(this.numerator, -power));
        }
        return new Rational((int) Math.pow(this.numerator, power), (int) Math.pow(this.denominator, power));
    }

    double exp(double exponent) {
        return Math.pow(this.numerator, exponent) / Math.pow(this.denominator, exponent);
    }

    double pow(double base) {
        return Math.pow(base, (double) this.numerator / this.denominator);
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
