import static java.util.Collections.unmodifiableList;

import java.util.ArrayList;
import java.util.List;
import org.json.JSONObject;

/** POJO representing a User in the database. */
public class User {
    private final String name;
    private final List<Iou> owes;
    private final List<Iou> owedBy;

    private User(String name, List<Iou> owes, List<Iou> owedBy) {
        this.name = name;
        this.owes = new ArrayList<>(owes);
        this.owedBy = new ArrayList<>(owedBy);
    }

    public String name() {
        return name;
    }

    /** IOUs this user owes to other users. */
    public List<Iou> owes() {
        return unmodifiableList(owes);
    }

    /** IOUs other users owe to this user. */
    public List<Iou> owedBy() {
        return unmodifiableList(owedBy);
    }

    public double balance() {
        double totalOwedBy = 0.0;
        for (Iou iou : owedBy) {
            totalOwedBy += iou.amount();
        }
        double totalOwes = 0.0;
        for (Iou iou : owes) {
            totalOwes += iou.amount();
        }
        return totalOwedBy - totalOwes;
    }

    public JSONObject toJSONObject() {
        JSONObject json = new JSONObject();
        json.put("name", name);
        
        JSONObject owesJson = new JSONObject();
        for (Iou iou : owes) {
            owesJson.put(iou.name(), iou.amount());
        }
        json.put("owes", owesJson);
        
        JSONObject owedByJson = new JSONObject();
        for (Iou iou : owedBy) {
            owedByJson.put(iou.name(), iou.amount());
        }
        json.put("owed_by", owedByJson);
        
        json.put("balance", balance());
        
        return json;
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String name;
        private final List<Iou> owes = new ArrayList<>();
        private final List<Iou> owedBy = new ArrayList<>();

        public Builder setName(String name) {
            this.name = name;
            return this;
        }

        public Builder owes(String name, double amount) {
            owes.add(new Iou(name, amount));
            return this;
        }

        public Builder owes(List<Iou> owes) {
            this.owes.addAll(owes);
            return this;
        }

        public Builder owedBy(String name, double amount) {
            owedBy.add(new Iou(name, amount));
            return this;
        }

        public Builder owedBy(List<Iou> owedBy) {
            this.owedBy.addAll(owedBy);
            return this;
        }

        public User build() {
            return new User(name, owes, owedBy);
        }
    }

    public static class Iou {
        private final String name;
        private final double amount;

        public Iou(String name, double amount) {
            this.name = name;
            this.amount = amount;
        }

        public String name() {
            return name;
        }

        public double amount() {
            return amount;
        }
    }
}
