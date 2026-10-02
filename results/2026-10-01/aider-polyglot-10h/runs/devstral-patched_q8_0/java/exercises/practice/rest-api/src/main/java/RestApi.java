import org.json.JSONObject;
import org.json.JSONArray;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;
import java.util.Collections;
import java.util.Comparator;

class RestApi {
    private final Map<String, User> users = new HashMap<>();

    RestApi(User... initialUsers) {
        for (User user : initialUsers) {
            users.put(user.name(), user);
        }
    }

    String get(String url) {
        if (url.equals("/users")) {
            List<User> allUsers = new ArrayList<>(users.values());
            Collections.sort(allUsers, Comparator.comparing(User::name));
            return formatUsersResponse(allUsers);
        }
        throw new UnsupportedOperationException("Unsupported URL: " + url);
    }

    String get(String url, JSONObject payload) {
        if (url.equals("/users")) {
            JSONArray userNames = payload.getJSONArray("users");
            List<User> requestedUsers = new ArrayList<>();
            for (int i = 0; i < userNames.length(); i++) {
                String name = userNames.getString(i);
                if (users.containsKey(name)) {
                    requestedUsers.add(users.get(name));
                }
            }
            Collections.sort(requestedUsers, Comparator.comparing(User::name));
            return formatUsersResponse(requestedUsers);
        }
        throw new UnsupportedOperationException("Unsupported URL: " + url);
    }

    String post(String url, JSONObject payload) {
        if (url.equals("/add")) {
            String userName = payload.getString("user");
            if (users.containsKey(userName)) {
                throw new IllegalArgumentException("User already exists");
            }
            User newUser = User.builder().setName(userName).build();
            users.put(userName, newUser);
            return newUser.toJson().toString();
        } else if (url.equals("/iou")) {
            String lender = payload.getString("lender");
            String borrower = payload.getString("borrower");
            double amount = payload.getDouble("amount");

            if (!users.containsKey(lender) || !users.containsKey(borrower)) {
                throw new IllegalArgumentException("One or both users don't exist");
            }

            // Update the borrower's owes list
            User borrowerUser = users.get(borrower);
            List<Iou> updatedOwes = new ArrayList<>(borrowerUser.owes());
            updatedOwes.add(new Iou(lender, amount));

            // Update the lender's owedBy list
            User lenderUser = users.get(lender);
            List<Iou> updatedOwedBy = new ArrayList<>(lenderUser.owedBy());
            updatedOwedBy.add(new Iou(borrower, amount));

            // Create updated users
            User updatedBorrower = User.builder()
                .setName(borrowerUser.name())
                .owesFromList(updatedOwes)
                .owedByFromList(borrowerUser.owedBy())
                .build();

            User updatedLender = User.builder()
                .setName(lenderUser.name())
                .owesFromList(lenderUser.owes())
                .owedByFromList(updatedOwedBy)
                .build();

            users.put(borrower, updatedBorrower);
            users.put(lender, updatedLender);

            List<User> responseUsers = new ArrayList<>();
            responseUsers.add(updatedBorrower);
            responseUsers.add(updatedLender);
            Collections.sort(responseUsers, Comparator.comparing(User::name));

            return formatUsersResponse(responseUsers);
        }
        throw new UnsupportedOperationException("Unsupported URL: " + url);
    }

    private String formatUsersResponse(List<User> users) {
        JSONObject response = new JSONObject();
        JSONArray usersArray = new JSONArray();
        for (User user : users) {
            usersArray.put(user.toJson());
        }
        response.put("users", usersArray);
        return response.toString();
    }
}
