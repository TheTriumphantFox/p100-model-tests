import static java.util.Collections.unmodifiableMap;

import java.util.Map;
import java.util.HashMap;
import org.json.JSONObject;
import org.json.JSONArray;

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
        return unmodifiableMap(owes);
    }

    /** IOUs other users owe to this user. */
    public Map<String, Double> owedBy() {
        return unmodifiableMap(owedBy);
    }

    public double balance() {
        double totalOwedBy = owedBy.values().stream().mapToDouble(Double::doubleValue).sum();
        double totalOwes = owes.values().stream().mapToDouble(Double::doubleValue).sum();
        return totalOwedBy - totalOwes;
    }

    public JSONObject toJson() {
        JSONObject obj = new JSONObject();
        obj.put("name", name);

        JSONObject owesObj = new JSONObject();
        for (Map.Entry<String, Double> e : owes.entrySet()) {
            owesObj.put(e.getKey(), e.getValue());
        }
        obj.put("owes", owesObj);

        JSONObject owedByObj = new JSONObject();
        for (Map.Entry<String, Double> e : owedBy.entrySet()) {
            owedByObj.put(e.getKey(), e.getValue());
        }
        obj.put("owed_by", owedByObj);

        obj.put("balance", balance());
        return obj;
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
            owes.merge(name, amount, Double::sum);
            return this;
        }

        public Builder owedBy(String name, double amount) {
            owedBy.merge(name, amount, Double::sum);
            return this;
        }

        public User build() {
            return new User(name, owes, owedBy);
        }
    }

    // Helper methods for RestApi to modify maps
    void addOwes(String name, double amount) {
        owes.merge(name, amount, Double::sum);
    }

    void addOwedBy(String name, double amount) {
        owedBy.merge(name, amount, Double::sum);
    }
}
