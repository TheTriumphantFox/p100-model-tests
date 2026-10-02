import org.json.JSONObject;
import org.json.JSONArray;

import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.stream.Collectors;

class RestApi {

    private final Map<String, User> users = new HashMap<>();

    RestApi(User... users) {
        for (User u : users) {
            this.users.put(u.name(), u);
        }
    }

    String get(String url) {
        if ("/users".equals(url)) {
            return listAllUsers();
        }
        throw new UnsupportedOperationException("Unsupported GET URL: " + url);
    }

    String get(String url, JSONObject payload) {
        if ("/users".equals(url)) {
            return listFilteredUsers(payload);
        }
        throw new UnsupportedOperationException("Unsupported GET URL: " + url);
    }

    String post(String url, JSONObject payload) {
        switch (url) {
            case "/add":
                return addUser(payload);
            case "/iou":
                return addIou(payload);
            default:
                throw new UnsupportedOperationException("Unsupported POST URL: " + url);
        }
    }

    private String listAllUsers() {
        JSONArray arr = new JSONArray();
        for (User u : users.values()) {
            arr.put(u.toJson());
        }
        JSONObject res = new JSONObject();
        res.put("users", arr);
        return res.toString();
    }

    private String listFilteredUsers(JSONObject payload) {
        JSONArray requested = payload.getJSONArray("users");
        List<String> names = new ArrayList<>();
        for (int i = 0; i < requested.length(); i++) {
            names.add(requested.getString(i));
        }
        List<User> filtered = names.stream()
                .map(users::get)
                .filter(u -> u != null)
                .sorted((a, b) -> a.name().compareTo(b.name()))
                .collect(Collectors.toList());
        JSONArray arr = new JSONArray();
        for (User u : filtered) {
            arr.put(u.toJson());
        }
        JSONObject res = new JSONObject();
        res.put("users", arr);
        return res.toString();
    }

    private String addUser(JSONObject payload) {
        String name = payload.getString("user");
        if (users.containsKey(name)) {
            throw new IllegalArgumentException("User already exists: " + name);
        }
        User newUser = User.builder().setName(name).build();
        users.put(name, newUser);
        return newUser.toJson().toString();
    }

    private String addIou(JSONObject payload) {
        String lender = payload.getString("lender");
        String borrower = payload.getString("borrower");
        double amount = payload.getDouble("amount");

        User lenderUser = users.get(lender);
        User borrowerUser = users.get(borrower);
        if (lenderUser == null || borrowerUser == null) {
            throw new IllegalArgumentException("Unknown user(s) in IOU");
        }

        // borrower owes lender
        borrowerUser.addOwes(lender, amount);
        lenderUser.addOwedBy(borrower, amount);

        JSONArray arr = new JSONArray();
        arr.put(lenderUser.toJson());
        arr.put(borrowerUser.toJson());
        JSONObject res = new JSONObject();
        res.put("users", arr);
        return res.toString();
    }
}
