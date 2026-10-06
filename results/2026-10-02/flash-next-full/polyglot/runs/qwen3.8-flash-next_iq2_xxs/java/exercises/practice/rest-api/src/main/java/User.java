import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

/** POJO representing a User in the database. */
public class User {
    private final String name;
    private final Map<String, Double> owes;
    private final Map<String, Double> owedBy;

    private User(String name, Map<String, Double> owes, Map<String, Double> owedBy) {
        this.name = name;
        this.owes = new HashMap<>(owes);
        this.owedBy = new HashMap<>(owedBy);
    }

    public String name() {
        return name;
    }

    /** IOUs this user owes to other users. */
    public Map<String, Double> owes() {
        return Map.copyOf(owes);
    }

    /** IOUs other users owe to this user. */
    public Map<String, Double> owedBy() {
        return Map.copyOf(owedBy);
    }

    public void owe(String name, double amount) {
        double currentOwedBy = owedBy.getOrDefault(name, 0.0);
        double newOwes = amount - currentOwedBy;
        if (newOwes > 0) {
            owes.put(name, newOwes);
            owedBy.remove(name);
        } else if (newOwes < 0) {
            owedBy.put(name, -newOwes);
            owes.remove(name);
        } else {
            owes.remove(name);
            owedBy.remove(name);
        }
    }

    public void beOwedBy(String name, double amount) {
        double currentOwes = owes.getOrDefault(name, 0.0);
        double newOwedBy = amount - currentOwes;
        if (newOwedBy > 0) {
            owedBy.put(name, newOwedBy);
            owes.remove(name);
        } else if (newOwedBy < 0) {
            owes.put(name, -newOwedBy);
            owedBy.remove(name);
        } else {
            owes.remove(name);
            owedBy.remove(name);
        }
    }

    public String toJson() {
        StringBuilder sb = new StringBuilder();
        sb.append("{\"owes\":{");
        appendMap(sb, owes);
        sb.append("},\"balance\":");
        double balance = 0.0;
        for (Double amount : owedBy.values()) {
            balance += amount;
        }
        for (Double amount : owes.values()) {
            balance -= amount;
        }
        sb.append(formatDouble(balance));
        sb.append(",\"name\":\"").append(name).append("\",");
        sb.append("\"owedBy\":{");
        appendMap(sb, owedBy);
        sb.append("}}");
        return sb.toString();
    }

    private void appendMap(StringBuilder sb, Map<String, Double> map) {
        TreeMap<String, Double> sortedMap = new TreeMap<>(map);
        boolean first = true;
        for (Map.Entry<String, Double> entry : sortedMap.entrySet()) {
            if (!first) {
                sb.append(",");
            }
            sb.append("\"").append(entry.getKey()).append("\":").append(formatDouble(entry.getValue()));
            first = false;
        }
    }

    private String formatDouble(double value) {
        if (value == (long) value) {
            return String.valueOf((long) value);
        } else {
            return String.valueOf(value);
        }
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String name;
        private final Map<String, Double> owes = new HashMap<>();
        private final Map<String, Double> owedBy = new HashMap<>();

        public Builder setName(String name) {
            this.name = name;
            return this;
        }

        public Builder owes(String name, double amount) {
            owes.put(name, amount);
            return this;
        }

        public Builder owedBy(String name, double amount) {
            owedBy.put(name, amount);
            return this;
        }

        public User build() {
            return new User(name, owes, owedBy);
        }
    }
}
