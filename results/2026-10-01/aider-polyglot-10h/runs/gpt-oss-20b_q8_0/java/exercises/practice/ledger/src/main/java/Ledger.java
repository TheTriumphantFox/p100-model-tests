import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Refactored Ledger printer.
 *
 * <p>Log of changes:
 * <ul>
 *   <li>Introduced {@code LocaleConfig} enum to encapsulate locale‑specific formatting
 *       (date pattern, decimal separator, thousand separator, currency symbol, header).</li>
 *   <li>Introduced {@code CurrencyConfig} enum to encapsulate currency‑specific symbols.</li>
 *   <li>Extracted validation logic into {@code validateInputs} method.</li>
 *   <li>Separated entry sorting into {@code sortEntries} method.</li>
 *   <li>Separated line formatting into {@code formatEntryLine} method.</li>
 *   <li>Replaced manual string building with {@link StringBuilder} for performance.</li>
 *   <li>Removed redundant null checks and unused variables.</li>
 *   <li>Added Javadoc comments for public API.</li>
 *   <li>Kept public method signatures unchanged to preserve compatibility with tests.</li>
 * </ul>
 */
public class Ledger {

    /**
     * Creates a {@link LedgerEntry} from the supplied parameters.
     *
     * @param d    date string in ISO format (yyyy-MM-dd)
     * @param desc description of the entry
     * @param c    change in cents (negative for debit, positive for credit)
     * @return a populated {@link LedgerEntry}
     */
    public LedgerEntry createLedgerEntry(String d, String desc, int c) {
        LedgerEntry le = new LedgerEntry();
        le.setChange(c);
        le.setDescription(desc);
        le.setLocalDate(LocalDate.parse(d));
        return le;
    }

    /**
     * Formats an array of {@link LedgerEntry} objects into a ledger string.
     *
     * @param cur     currency code ("USD" or "EUR")
     * @param loc     locale ("en-US" or "nl-NL")
     * @param entries array of entries to format
     * @return formatted ledger string
     */
    public String format(String cur, String loc, LedgerEntry[] entries) {
        validateInputs(cur, loc);

        LocaleConfig locale = LocaleConfig.from(loc);
        CurrencyConfig currency = CurrencyConfig.from(cur);

        StringBuilder sb = new StringBuilder();
        sb.append(locale.header);

        if (entries.length == 0) {
            return sb.toString();
        }

        List<LedgerEntry> sorted = sortEntries(entries);
        for (LedgerEntry e : sorted) {
            sb.append('\n');
            sb.append(formatEntryLine(e, locale, currency));
        }

        return sb.toString();
    }

    /* --------------------------------------------------------------------- */
    /* Helper methods                                                        */
    /* --------------------------------------------------------------------- */

    private void validateInputs(String cur, String loc) {
        if (!CurrencyConfig.isValid(cur)) {
            throw new IllegalArgumentException("Invalid currency");
        }
        if (!LocaleConfig.isValid(loc)) {
            throw new IllegalArgumentException("Invalid locale");
        }
    }

    private List<LedgerEntry> sortEntries(LedgerEntry[] entries) {
        List<LedgerEntry> neg = new ArrayList<>();
        List<LedgerEntry> pos = new ArrayList<>();

        for (LedgerEntry e : entries) {
            if (e.getChange() >= 0) {
                pos.add(e);
            } else {
                neg.add(e);
            }
        }

        Comparator<LedgerEntry> byDate = Comparator.comparing(LedgerEntry::getLocalDate);
        neg.sort(byDate);
        pos.sort(byDate);

        List<LedgerEntry> all = new ArrayList<>();
        all.addAll(neg);
        all.addAll(pos);
        return all;
    }

    private String formatEntryLine(LedgerEntry e, LocaleConfig locale, CurrencyConfig currency) {
        String date = e.getLocalDate().format(DateTimeFormatter.ofPattern(locale.datePattern));

        String desc = e.getDescription();
        if (desc.length() > 25) {
            desc = desc.substring(0, 22) + "...";
        }

        // Convert cents to formatted string
        double amountCents = e.getChange() / 100.0;
        String formatted = String.format(locale.decimalFormat, Math.abs(amountCents));

        // Insert thousand separators
        String[] parts = formatted.split("\\.");
        String integerPart = parts[0];
        String decimalPart = parts[1];

        StringBuilder intBuilder = new StringBuilder();
        int count = 0;
        for (int i = integerPart.length() - 1; i >= 0; i--) {
            intBuilder.insert(0, integerPart.charAt(i));
            count++;
            if (count % 3 == 0 && i != 0) {
                intBuilder.insert(0, locale.thousandSeparator);
            }
        }

        String amount = currency.symbol + intBuilder + locale.decimalSeparator + decimalPart;

        // Adjust spacing and sign formatting
        if (e.getChange() < 0) {
            if (locale.isEnglish()) {
                amount = "(" + amount + ")";
            } else {
                // Dutch style: symbol + space + negative sign
                amount = currency.symbol + " -" + intBuilder + locale.decimalSeparator + decimalPart + " ";
            }
        } else {
            // Positive amounts get a leading space for both locales
            amount = " " + amount;
            if (!locale.isEnglish()) {
                // Dutch style: add trailing space
                amount = amount + " ";
            }
        }

        return String.format("%s | %-25s | %13s", date, desc, amount);
    }

    /* --------------------------------------------------------------------- */
    /* Configuration enums                                                  */
    /* --------------------------------------------------------------------- */

    private enum LocaleConfig {
        EN_US("en-US", "MM/dd/yyyy", ".", ",", "$", "Date       | Description               | Change       "),
        NL_NL("nl-NL", "dd/MM/yyyy", ",", ".", "€", "Datum      | Omschrijving              | Verandering  ");

        final String code;
        final String datePattern;
        final String decimalSeparator;
        final String thousandSeparator;
        final String currencySymbol;
        final String header;
        final String decimalFormat = "%,.2f";

        LocaleConfig(String code, String datePattern, String decimalSeparator,
                     String thousandSeparator, String currencySymbol, String header) {
            this.code = code;
            this.datePattern = datePattern;
            this.decimalSeparator = decimalSeparator;
            this.thousandSeparator = thousandSeparator;
            this.currencySymbol = currencySymbol;
            this.header = header;
        }

        static LocaleConfig from(String code) {
            for (LocaleConfig lc : values()) {
                if (lc.code.equals(code)) {
                    return lc;
                }
            }
            throw new IllegalArgumentException("Unsupported locale");
        }

        static boolean isValid(String code) {
            for (LocaleConfig lc : values()) {
                if (lc.code.equals(code)) {
                    return true;
                }
            }
            return false;
        }

        boolean isEnglish() {
            return this == EN_US;
        }
    }

    private enum CurrencyConfig {
        USD("USD", "$"),
        EUR("EUR", "€");

        final String code;
        final String symbol;

        CurrencyConfig(String code, String symbol) {
            this.code = code;
            this.symbol = symbol;
        }

        static CurrencyConfig from(String code) {
            for (CurrencyConfig cc : values()) {
                if (cc.code.equals(code)) {
                    return cc;
                }
            }
            throw new IllegalArgumentException("Unsupported currency");
        }

        static boolean isValid(String code) {
            for (CurrencyConfig cc : values()) {
                if (cc.code.equals(code)) {
                    return true;
                }
            }
            return false;
        }
    }

    /* --------------------------------------------------------------------- */
    /* LedgerEntry inner class                                               */
    /* --------------------------------------------------------------------- */

    public static class LedgerEntry {
        private LocalDate localDate;
        private String description;
        private double change;

        public LocalDate getLocalDate() {
            return localDate;
        }

        public void setLocalDate(LocalDate localDate) {
            this.localDate = localDate;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }

        public double getChange() {
            return change;
        }

        public void setChange(double change) {
            this.change = change;
        }
    }
}
