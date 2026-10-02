import org.json.JSONObject;
import org.json.JSONArray;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

class RestApi {

    private final List<User> users;

    RestApi(User... users) {
        this.users = new ArrayList<>();
        for (User u : users) {
            this.users.add(u);
        }
    }

    String get(String url) {
        return get(url, null);
    }

    String get(String url, JSONObject payload) {
        if (url.equals("/users")) {
            List<String> names = null;
            if (payload != null && payload.has("users")) {
                JSONArray namesArray = payload.getJSONArray("users");
                names = new ArrayList<>();
                for (int i = 0; i < namesArray.length(); i++) {
                    names.add(namesArray.getString(i));
                }
            }

            List<User> resultUsers;
            if (names == null) {
                resultUsers = new ArrayList<>(users);
            } else {
                resultUsers = users.stream()
                        .filter(u -> names.contains(u.name()))
                        .collect(Collectors.toList());
            }

            resultUsers.sort(Comparator.comparing(User::name));

            JSONObject response = new JSONObject();
            JSONArray usersArray = new JSONArray();
            for (User u : resultUsers) {
                usersArray.put(u.toJSONObject());
            }
            response.put("users", usersArray);
            return response.toString();
        }
        return "{}";
    }

    String post(String url, JSONObject payload) {
        if (url.equals("/add")) {
            String name = payload.getString("user");
            User newUser = User.builder().setName(name).build();
            users.add(newUser);
            return newUser.toJSONObject().toString();
        } else if (url.equals("/iou")) {
            String lenderName = payload.getString("lender");
            String borrowerName = payload.getString("borrower");
            double amount = payload.getDouble("amount");

            User lender = users.stream().filter(u -> u.name().equals(lenderName)).findFirst().orElse(null);
            User borrower = users.stream().filter(u -> u.name().equals(borrowerName)).findFirst().orElse(null);

            if (lender == null || borrower == null) {
                return "{}"; // Or handle error appropriately
            }

            // Update lender: owedBy borrower
            // Update borrower: owes lender
            
            // We need to rebuild the users with updated IOUs
            List<User> updatedUsers = new ArrayList<>();
            for (User u : users) {
                if (u.name().equals(lenderName)) {
                    updatedUsers.add(updateUserOwedBy(u, borrowerName, amount));
                } else if (u.name().equals(borrowerName)) {
                    updatedUsers.add(updateUserOwes(u, lenderName, amount));
                } else {
                    updatedUsers.add(u);
                }
            }
            
            // Replace users list
            users.clear();
            users.addAll(updatedUsers);

            // Return updated lender and borrower sorted by name
            List<User> resultUsers = new ArrayList<>();
            resultUsers.add(users.stream().filter(u -> u.name().equals(lenderName)).findFirst().get());
            resultUsers.add(users.stream().filter(u -> u.name().equals(borrowerName)).findFirst().get());
            resultUsers.sort(Comparator.comparing(User::name));

            JSONObject response = new JSONObject();
            JSONArray usersArray = new JSONArray();
            for (User u : resultUsers) {
                usersArray.put(u.toJSONObject());
            }
            response.put("users", usersArray);
            return response.toString();
        }
        return "{}";
    }

    private User updateUserOwes(User user, String name, double amount) {
        List<User.Iou> newOwes = new ArrayList<>();
        boolean found = false;
        for (User.Iou iou : user.owes()) {
            if (iou.name().equals(name)) {
                newOwes.add(new User.Iou(name, iou.amount() + amount));
                found = true;
            } else {
                newOwes.add(iou);
            }
        }
        if (!found) {
            newOwes.add(new User.Iou(name, amount));
        }
        
        return User.builder()
                .setName(user.name())
                .owes(newOwes)
                .owedBy(user.owedBy())
                .build();
    }

    private User updateUserOwedBy(User user, String name, double amount) {
        List<User.Iou> newOwedBy = new ArrayList<>();
        boolean found = false;
        for (User.Iou iou : user.owedBy()) {
            if (iou.name().equals(name)) {
                newOwedBy.add(new User.Iou(name, iou.amount() + amount));
                found = true;
            } else {
                newOwedBy.add(iou);
            }
        }
        if (!found) {
            newOwedBy.add(new User.Iou(name, amount));
        }

        return User.builder()
                .setName(user.name())
                .owes(user.owes())
                .owedBy(newOwedBy)
                .build();
    }
}
