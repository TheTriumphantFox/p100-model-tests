import static java.util.Collections.unmodifiableList;

import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Map;
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

    /** Calculate the user's balance (total owed by others minus total owed to others) */
    public double balance() {
        double totalOwedBy = 0.0;
        for (Iou iou : owedBy) {
            totalOwedBy += iou.getAmount();
        }

        double totalOwes = 0.0;
        for (Iou iou : owes) {
            totalOwes += iou.getAmount();
        }

        return totalOwedBy - totalOwes;
    }

    /** Convert user to JSON format */
    public JSONObject toJson() {
        JSONObject userJson = new JSONObject();
        userJson.put("name", name);

        // Create owes map
        JSONObject owesMap = new JSONObject();
        for (Iou iou : owes) {
            owesMap.put(iou.getTo(), iou.getAmount());
        }
        userJson.put("owes", owesMap);

        // Create owed_by map
        JSONObject owedByMap = new JSONObject();
        for (Iou iou : owedBy) {
            owedByMap.put(iou.getTo(), iou.getAmount());
        }
        userJson.put("owed_by", owedByMap);

        userJson.put("balance", balance());

        return userJson;
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

        public Builder owedBy(String name, double amount) {
            owedBy.add(new Iou(name, amount));
            return this;
        }

        /** Alternative method to set owes from existing list */
        public Builder owesFromList(List<Iou> ious) {
            owes.clear();
            owes.addAll(ious);
            return this;
        }

        /** Alternative method to set owedBy from existing list */
        public Builder owedByFromList(List<Iou> ious) {
            owedBy.clear();
            owedBy.addAll(ious);
            return this;
        }

        public User build() {
            return new User(name, owes, owedBy);
        }
    }
}
