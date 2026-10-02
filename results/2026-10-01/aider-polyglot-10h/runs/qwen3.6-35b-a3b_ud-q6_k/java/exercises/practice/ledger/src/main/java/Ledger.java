import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class Ledger {
    public LedgerEntry createLedgerEntry(String d, String desc, int c) {
        LedgerEntry le = new LedgerEntry();
        le.setChange(c);
        le.setDescription(desc);
        le.setLocalDate(LocalDate.parse(d));
        return le;
    }

    public String format(String cur, String loc, LedgerEntry[] entries) {
        if (!cur.equals("USD") && !cur.equals("EUR")) {
            throw new IllegalArgumentException("Invalid currency");
        } else if (!loc.equals("en-US") && !loc.equals("nl-NL")) {
            throw new IllegalArgumentException("Invalid locale");
        }

        LedgerConfiguration config = new LedgerConfiguration(cur, loc);
        StringBuilder sb = new StringBuilder();
        sb.append(config.header);

        if (entries.length == 0) {
            return sb.toString();
        }

        List<LedgerEntry> sortedEntries = new ArrayList<>();
        for (LedgerEntry entry : entries) {
            sortedEntries.add(entry);
        }

        // Sort: Negative changes first, then positive. Within each group, sort by date.
        sortedEntries.sort(Comparator.comparingDouble(LedgerEntry::getChange)
                .thenComparing(LedgerEntry::getLocalDate));

        DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern(config.datePattern);

        for (LedgerEntry entry : sortedEntries) {
            sb.append("\n");
            
            // Date
            String dateStr = entry.getLocalDate().format(dateFormatter);
            sb.append(dateStr).append(" | ");

            // Description
            String desc = entry.getDescription();
            if (desc.length() > 25) {
                desc = desc.substring(0, 22) + "...";
            }
            sb.append(String.format("%-25s", desc)).append(" | ");

            // Amount
            String amountStr = formatAmount(entry.getChange(), config);
            sb.append(String.format("%13s", amountStr));
        }

        return sb.toString();
    }

    private String formatAmount(double change, LedgerConfiguration config) {
        String symbol = config.currencySymbol;
        String decSep = config.decimalSeparator;
        String thSep = config.thousandsSeparator;
        boolean isNegative = change < 0;
        
        // Calculate absolute value in cents to avoid floating point issues
        long absCents = Math.abs((long) change);
        long dollars = absCents / 100;
        int cents = (int) (absCents % 100);

        // Format dollars with thousands separator
        String dollarsStr = String.valueOf(dollars);
        StringBuilder formattedDollars = new StringBuilder();
        int len = dollarsStr.length();
        for (int i = 0; i < len; i++) {
            if (i > 0 && (len - i) % 3 == 0) {
                formattedDollars.append(thSep);
            }
            formattedDollars.append(dollarsStr.charAt(i));
        }

        String amountPart = symbol + (config.locale.equals("nl-NL") ? " " : "") + formattedDollars + decSep + String.format("%02d", cents);

        if (isNegative) {
            if (config.locale.equals("en-US")) {
                return "(" + amountPart + ")";
            } else {
                // nl-NL: € -1.234,56
                return symbol + " -" + formattedDollars + decSep + String.format("%02d", cents) + " ";
            }
        } else {
            if (config.locale.equals("nl-NL")) {
                return " " + amountPart + " ";
            } else {
                return amountPart + " ";
            }
        }
    }

    private static class LedgerConfiguration {
        final String header;
        final String currencySymbol;
        final String datePattern;
        final String decimalSeparator;
        final String thousandsSeparator;
        final String locale;

        public LedgerConfiguration(String currency, String locale) {
            this.locale = locale;
            boolean isUSD = currency.equals("USD");
            boolean isEnUS = locale.equals("en-US");

            if (isUSD) {
                this.currencySymbol = "$";
            } else {
                this.currencySymbol = "€";
            }

            if (isEnUS) {
                this.header = "Date       | Description               | Change       ";
                this.datePattern = "MM/dd/yyyy";
                this.decimalSeparator = ".";
                this.thousandsSeparator = ",";
            } else {
                this.header = "Datum      | Omschrijving              | Verandering  ";
                this.datePattern = "dd/MM/yyyy";
                this.decimalSeparator = ",";
                this.thousandsSeparator = ".";
            }
        }
    }

    public static class LedgerEntry {
        LocalDate localDate;
        String description;
        double change;

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
