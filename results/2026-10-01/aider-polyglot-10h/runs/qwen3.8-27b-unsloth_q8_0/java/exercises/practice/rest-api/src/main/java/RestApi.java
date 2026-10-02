import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class RestApi {

    private final Map<String, User> users;

    RestApi(User... users) {
        this.users = new HashMap<>();
        for (User user : users) {
            this.users.put(user.name(), user);
        }
    }

    String get(String url) {
        return get(url, null);
    }

    String get(String url, JSONObject payload) {
        if (url.equals("/users")) {
            List<User> userList = new ArrayList<>(users.values());
            Collections.sort(userList, (u1, u2) -> u1.name().compareTo(u2.name()));

            if (payload != null && payload.has("users")) {
                JSONArray userNames = payload.getJSONArray("users");
                List<String> requestedNames = new ArrayList<>();
                for (int i = 0; i < userNames.length(); i++) {
                    requestedNames.add(userNames.getString(i));
                }
                
                List<User> filteredUsers = new ArrayList<>();
                for (User user : userList) {
                    if (requestedNames.contains(user.name())) {
                        filteredUsers.add(user);
                    }
                }
                userList = filteredUsers;
            }

            JSONArray usersJsonArray = new JSONArray();
            for (User user : userList) {
                usersJsonArray.put(user.toJson());
            }
            
            JSONObject response = new JSONObject();
            response.put("users", usersJsonArray);
            return response.toString();
        }
        
        return "{}";
    }

    String post(String url, JSONObject payload) {
        if (url.equals("/add")) {
            String name = payload.getString("user");
            if (users.containsKey(name)) {
                return "{}"; 
            }
            User newUser = User.builder().setName(name).build();
            users.put(name, newUser);
            return newUser.toJson().toString();
        } else if (url.equals("/iou")) {
            String lenderName = payload.getString("lender");
            String borrowerName = payload.getString("borrower");
            double amount = payload.getDouble("amount");

            User lender = users.get(lenderName);
            User borrower = users.get(borrowerName);

            if (lender == null || borrower == null) {
                return "{}";
            }

            List<Iou> lenderOwes = new ArrayList<>(lender.owes());
            List<Iou> lenderOwedBy = new ArrayList<>(lender.owedBy());
            
            List<Iou> borrowerOwes = new ArrayList<>(borrower.owes());
            List<Iou> borrowerOwedBy = new ArrayList<>(borrower.owedBy());

            boolean foundLenderOwedBy = false;
            for (int i = 0; i < lenderOwedBy.size(); i++) {
                if (lenderOwedBy.get(i).name().equals(borrowerName)) {
                    lenderOwedBy.set(i, new Iou(borrowerName, lenderOwedBy.get(i).amount() + amount));
                    foundLenderOwedBy = true;
                    break;
                }
            }
            if (!foundLenderOwedBy) {
                lenderOwedBy.add(new Iou(borrowerName, amount));
            }

            boolean foundBorrowerOwes = false;
            for (int i = 0; i < borrowerOwes.size(); i++) {
                if (borrowerOwes.get(i).name().equals(lenderName)) {
                    borrowerOwes.set(i, new Iou(lenderName, borrowerOwes.get(i).amount() + amount));
                    foundBorrowerOwes = true;
                    break;
                }
            }
            if (!foundBorrowerOwes) {
                borrowerOwes.add(new Iou(lenderName, amount));
            }

            User updatedLender = User.create(lenderName, lenderOwes, lenderOwedBy);
            User updatedBorrower = User.create(borrowerName, borrowerOwes, borrowerOwedBy);
            
            users.put(lenderName, updatedLender);
            users.put(borrowerName, updatedBorrower);
            
            List<User> updatedUsers = new ArrayList<>();
            updatedUsers.add(updatedLender);
            updatedUsers.add(updatedBorrower);
            Collections.sort(updatedUsers, (u1, u2) -> u1.name().compareTo(u2.name()));
            
            JSONArray usersJsonArray = new JSONArray();
            for (User user : updatedUsers) {
                usersJsonArray.put(user.toJson());
            }
            
            JSONObject response = new JSONObject();
            response.put("users", usersJsonArray);
            return response.toString();
        }
        
        return "{}";
    }
}
