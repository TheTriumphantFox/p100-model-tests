import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
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
        String header;
        String curSymb;
        String datPat;
        String decSep;
        String thSep;

        if (!cur.equals("USD") && !cur.equals("EUR")) {
            throw new IllegalArgumentException("Invalid currency");
        }
        if (!loc.equals("en-US") && !loc.equals("nl-NL")) {
            throw new IllegalArgumentException("Invalid locale");
        }

        if (cur.equals("USD")) {
            curSymb = "$";
        } else {
            curSymb = "€";
        }

        if (loc.equals("en-US")) {
            datPat = "MM/dd/yyyy";
            decSep = ".";
            thSep = ",";
            header = "Date       | Description               | Change       ";
        } else {
            datPat = "dd/MM/yyyy";
            decSep = ",";
            thSep = ".";
            header = "Datum      | Omschrijving              | Verandering  ";
        }

        StringBuilder s = new StringBuilder(header);

        if (entries.length > 0) {
            List<LedgerEntry> neg = new ArrayList<>();
            List<LedgerEntry> pos = new ArrayList<>();
            for (LedgerEntry e : entries) {
                if (e.getChange() >= 0) {
                    pos.add(e);
                } else {
                    neg.add(e);
                }
            }

            neg.sort((o1, o2) -> o1.getLocalDate().compareTo(o2.getLocalDate()));
            pos.sort((o1, o2) -> o1.getLocalDate().compareTo(o2.getLocalDate()));

            List<LedgerEntry> all = new ArrayList<>();
            all.addAll(neg);
            all.addAll(pos);

            for (LedgerEntry e : all) {
                String date = e.getLocalDate().format(DateTimeFormatter.ofPattern(datPat));

                String desc = e.getDescription();
                if (desc.length() > 25) {
                    desc = desc.substring(0, 22) + "...";
                }

                double amountVal = e.getChange() / 100.0;
                String converted = String.format("%.2f", Math.abs(amountVal));

                String[] parts = converted.split("\\.");
                String amount = "";
                int count = 1;
                for (int ind = parts[0].length() - 1; ind >= 0; ind--) {
                    if (((count % 3) == 0) && ind > 0) {
                        amount = thSep + parts[0].charAt(ind) + amount;
                    } else {
                        amount = parts[0].charAt(ind) + amount;
                    }
                    count++;
                }

                String formattedAmount;
                if (loc.equals("nl-NL")) {
                    formattedAmount = curSymb + " " + amount + decSep + parts[1];
                } else {
                    formattedAmount = curSymb + amount + decSep + parts[1];
                }

                if (e.getChange() < 0 && loc.equals("en-US")) {
                    formattedAmount = "(" + formattedAmount + ")";
                } else if (e.getChange() < 0 && loc.equals("nl-NL")) {
                    formattedAmount = curSymb + " -" + formattedAmount.replace(curSymb, "").trim() + " ";
                } else if (loc.equals("nl-NL")) {
                    formattedAmount = " " + formattedAmount + " ";
                } else {
                    formattedAmount = formattedAmount + " ";
                }

                s.append("\n");
                s.append(String.format("%s | %-25s | %13s", date, desc, formattedAmount));
            }
        }

        return s.toString();
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
