import static java.util.Collections.unmodifiableList;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import org.json.JSONObject;

/** POJO representing a User in the database. */
public class User {
    private final String name;
    private final Map<String, Double> owes;
    private final Map<String, Double> owedBy;

    private User(String name, Map<String, Double> owes, Map<String, Double> owedBy) {
        this.name = name;
        this.owes = new TreeMap<>(owes);
        this.owedBy = new TreeMap<>(owedBy);
    }

    public String name() {
        return name;
    }

    /** IOUs this user owes to other users. */
    public List<Iou> owes() {
        List<Iou> list = new ArrayList<>();
        for (Map.Entry<String, Double> entry : owes.entrySet()) {
            list.add(new Iou(entry.getKey(), entry.getValue()));
        }
        return unmodifiableList(list);
    }

    /** IOUs other users owe to this user. */
    public List<Iou> owedBy() {
        List<Iou> list = new ArrayList<>();
        for (Map.Entry<String, Double> entry : owedBy.entrySet()) {
            list.add(new Iou(entry.getKey(), entry.getValue()));
        }
        return unmodifiableList(list);
    }

    public double balance() {
        double totalOwedBy = 0.0;
        for (double amount : owedBy.values()) {
            totalOwedBy += amount;
        }
        double totalOwes = 0.0;
        for (double amount : owes.values()) {
            totalOwes += amount;
        }
        return totalOwedBy - totalOwes;
    }

    public static Builder builder() {
        return new Builder();
    }

    public static User fromJson(JSONObject json) {
        String name = json.getString("name");
        Map<String, Double> owes = new HashMap<>();
        Map<String, Double> owedBy = new HashMap<>();

        if (json.has("owes")) {
            JSONObject owesJson = json.getJSONObject("owes");
            for (String key : owesJson.keySet()) {
                owes.put(key, owesJson.getDouble(key));
            }
        }

        if (json.has("owed_by")) {
            JSONObject owedByJson = json.getJSONObject("owed_by");
            for (String key : owedByJson.keySet()) {
                owedBy.put(key, owedByJson.getDouble(key));
            }
        }

        return new User(name, owes, owedBy);
    }

    public JSONObject toJson() {
        JSONObject json = new JSONObject();
        json.put("name", name);

        JSONObject owesJson = new JSONObject();
        for (Map.Entry<String, Double> entry : owes.entrySet()) {
            owesJson.put(entry.getKey(), entry.getValue());
        }
        json.put("owes", owesJson);

        JSONObject owedByJson = new JSONObject();
        for (Map.Entry<String, Double> entry : owedBy.entrySet()) {
            owedByJson.put(entry.getKey(), entry.getValue());
        }
        json.put("owed_by", owedByJson);

        json.put("balance", balance());

        return json;
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
            this.owes.merge(name, amount, Double::sum);
            return this;
        }

        public Builder owedBy(String name, double amount) {
            this.owedBy.merge(name, amount, Double::sum);
            return this;
        }

        public User build() {
            return new User(name, owes, owedBy);
        }
    }
}
