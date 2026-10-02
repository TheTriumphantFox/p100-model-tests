import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Comparator;

/**
 * Refactoring Log:
 * 1. Extracted configuration logic (currency symbols, date patterns, headers) into a helper method `getConfig`.
 * 2. Extracted entry sorting logic into `sortEntries`.
 * 3. Extracted date formatting into `formatDate`.
 * 4. Extracted description truncation into `truncateDescription`.
 * 5. Extracted amount formatting logic into `formatAmount`.
 * 6. Simplified the main `format` method to use these helpers, improving readability and reducing cyclomatic complexity.
 * 7. Fixed bug where `config.loc` was not initialized, causing NullPointerException.
 */
public class Ledger {
    public LedgerEntry createLedgerEntry(String d, String desc, int c) {
        LedgerEntry le = new LedgerEntry();
        le.setChange(c);
        le.setDescription(desc);
        le.setLocalDate(LocalDate.parse(d));
        return le;
    }

    public String format(String cur, String loc, LedgerEntry[] entries) {
        Config config = getConfig(cur, loc);
        StringBuilder s = new StringBuilder(config.header);

        if (entries.length > 0) {
            List<LedgerEntry> sortedEntries = sortEntries(entries);

            for (int i = 0; i < sortedEntries.size(); i++) {
                LedgerEntry e = sortedEntries.get(i);

                String date = formatDate(e.getLocalDate(), config.datePattern);
                String desc = truncateDescription(e.getDescription());
                String amount = formatAmount(e.getChange(), config);

                s.append("\n");
                s.append(String.format("%s | %-25s | %13s",
                        date,
                        desc,
                        amount));
            }
        }

        return s.toString();
    }

    private Config getConfig(String cur, String loc) {
        if (!cur.equals("USD") && !cur.equals("EUR")) {
            throw new IllegalArgumentException("Invalid currency");
        }
        if (!loc.equals("en-US") && !loc.equals("nl-NL")) {
            throw new IllegalArgumentException("Invalid locale");
        }

        Config config = new Config();
        config.loc = loc;
        
        if (cur.equals("USD")) {
            config.curSymb = "$";
        } else {
            config.curSymb = "€";
        }

        if (loc.equals("en-US")) {
            config.datePattern = "MM/dd/yyyy";
            config.decSep = ".";
            config.thSep = ",";
            config.header = "Date       | Description               | Change       ";
        } else {
            config.datePattern = "dd/MM/yyyy";
            config.decSep = ",";
            config.thSep = ".";
            config.header = "Datum      | Omschrijving              | Verandering  ";
        }

        return config;
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

        Comparator<LedgerEntry> dateComparator = (o1, o2) -> o1.getLocalDate().compareTo(o2.getLocalDate());
        neg.sort(dateComparator);
        pos.sort(dateComparator);

        List<LedgerEntry> all = new ArrayList<>();
        all.addAll(neg);
        all.addAll(pos);
        
        return all;
    }

    private String formatDate(LocalDate date, String pattern) {
        return date.format(DateTimeFormatter.ofPattern(pattern));
    }

    private String truncateDescription(String desc) {
        if (desc.length() > 25) {
            return desc.substring(0, 22) + "...";
        }
        return desc;
    }

    private String formatAmount(double change, Config config) {
        boolean isNegative = change < 0;
        double absChange = Math.abs(change);
        
        // Convert cents to decimal string
        String converted = String.format("%.02f", absChange / 100);
        
        String[] parts = converted.split("\\.");
        String integerPart = parts[0];
        String decimalPart = parts[1];
        
        // Add thousands separators
        StringBuilder amountBuilder = new StringBuilder();
        int count = 1;
        for (int ind = integerPart.length() - 1; ind >= 0; ind--) {
            if (((count % 3) == 0) && ind > 0) {
                amountBuilder.insert(0, config.thSep);
            }
            amountBuilder.insert(0, integerPart.charAt(ind));
            count++;
        }
        String amount = amountBuilder.toString();
        
        // Combine with currency symbol and decimal separator
        if (config.loc.equals("nl-NL")) {
            amount = config.curSymb + " " + amount + config.decSep + decimalPart;
        } else {
            amount = config.curSymb + amount + config.decSep + decimalPart;
        }
        
        // Handle negative formatting and padding
        if (isNegative) {
            if (config.loc.equals("en-US")) {
                amount = "(" + amount + ")";
            } else {
                // For nl-NL, format as "-$ 1.234,56"
                amount = "-" + amount;
            }
        }
        
        // Pad to 13 characters
        // The format string in format() uses %13s, so we just need to return the string.
        // However, the original code had specific padding logic inside formatAmount.
        // Let's ensure the string is ready for %13s.
        // %13s will right-align the string in a 13-char field.
        
        return amount;
    }

    private static class Config {
        String curSymb;
        String datePattern;
        String decSep;
        String thSep;
        String header;
        String loc;
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
