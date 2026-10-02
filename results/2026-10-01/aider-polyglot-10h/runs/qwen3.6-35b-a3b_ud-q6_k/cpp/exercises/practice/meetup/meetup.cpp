#include "meetup.h"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>

namespace meetup {

namespace chrono = std::chrono;

std::string day(std::string schedule, std::string weekday, int year, int month) {
    // Map weekday string to weekday index (0=Sun, 1=Mon, ..., 6=Sat)
    int target_weekday = -1;
    if (weekday == "Monday") target_weekday = 1;
    else if (weekday == "Tuesday") target_weekday = 2;
    else if (weekday == "Wednesday") target_weekday = 3;
    else if (weekday == "Thursday") target_weekday = 4;
    else if (weekday == "Friday") target_weekday = 5;
    else if (weekday == "Saturday") target_weekday = 6;
    else if (weekday == "Sunday") target_weekday = 0;

    if (target_weekday == -1) return "";

    // Determine range of days to check based on schedule
    int start_day = 1;
    int end_day = 31; // Max days in a month

    if (schedule == "first") {
        start_day = 1;
        end_day = 7;
    } else if (schedule == "second") {
        start_day = 8;
        end_day = 14;
    } else if (schedule == "third") {
        start_day = 15;
        end_day = 21;
    } else if (schedule == "fourth") {
        start_day = 22;
        end_day = 28;
    } else if (schedule == "teenth") {
        start_day = 13;
        end_day = 19;
    } else if (schedule == "last") {
        // Find last day of month
        // Use chrono to get last day
        auto last_day_of_month = (chrono::year{year} / chrono::month{month} / chrono::day{1}).last();
        end_day = static_cast<int>(static_cast<unsigned>(last_day_of_month.day()));
        start_day = end_day - 6;
    }

    // Iterate through the range to find the correct weekday
    for (int d = start_day; d <= end_day; ++d) {
        // Construct date
        auto date = chrono::year{year} / chrono::month{month} / chrono::day{d};
        if (!date.ok()) continue; // Invalid date (e.g. Feb 30)

        // Get weekday
        // chrono::weekday is 0=Sun, 1=Mon, ...
        auto wd = chrono::weekday(date);
        if (static_cast<int>(wd) == target_weekday) {
            // Format as YYYY-MM-DD
            std::ostringstream oss;
            oss << std::setfill('0')
                << static_cast<int>(date.year()) << "-"
                << std::setw(2) << static_cast<unsigned>(date.month()) << "-"
                << std::setw(2) << static_cast<unsigned>(date.day());
            return oss.str();
        }
    }

    return "";
}

}  // namespace meetup
