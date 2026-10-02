#include "meetup.h"
#include <stdexcept>

namespace meetup {

scheduler::scheduler(int year, int month) : year_(year), month_(month) {}

int scheduler::meetup(week w, weekday d) {
    if (month_ < 1 || month_ > 12) {
        throw std::invalid_argument("Invalid month");
    }

    // Determine days in month
    int days_in_month;
    switch (month_) {
        case 1: case 3: case 5: case 7: case 8: case 10: case 12:
            days_in_month = 31;
            break;
        case 4: case 6: case 9: case 11:
            days_in_month = 30;
            break;
        case 2:
            // Leap year check
            if ((year_ % 4 == 0 && year_ % 100 != 0) || (year_ % 400 == 0)) {
                days_in_month = 29;
            } else {
                days_in_month = 28;
            }
            break;
        default:
            throw std::invalid_argument("Invalid month");
    }

    // Map weekday enum to 0-6 (0=Monday, 1=Tuesday, ..., 6=Sunday)
    // This matches our enum order: monday=0, ..., sunday=6
    int target_wday = static_cast<int>(d);

    // Calculate the day of the week for the 1st of the month.
    // We use a known reference: Jan 1, 1900 was a Monday (0).
    // We calculate the total number of days from Jan 1, 1900 to the 1st of the given month/year.
    
    int y = year_;
    int m = month_;
    
    // If month is Jan or Feb, we consider the previous year for leap year calculations in the loop
    if (m <= 2) {
        y--;
    }
    
    long days = 0;
    
    // Days from 1900 to y
    for (int i = 1900; i < y; ++i) {
        if ((i % 4 == 0 && i % 100 != 0) || (i % 400 == 0)) {
            days += 366;
        } else {
            days += 365;
        }
    }
    
    // Days from start of year y to start of month m
    static const int days_in_month_non_leap[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    for (int i = 1; i < m; ++i) {
        days += days_in_month_non_leap[i - 1];
        if (i == 2 && ((y % 4 == 0 && y % 100 != 0) || (y % 400 == 0))) {
            days += 1;
        }
    }
    
    // Jan 1, 1900 was Monday (0).
    // So the weekday of the 1st of the current month is (0 + days) % 7
    int first_day_wday = days % 7;

    int result_day = -1;

    if (w == week::teenth) {
        // Check days 13 to 19
        for (int day = 13; day <= 19; ++day) {
            int wday = (first_day_wday + day - 1) % 7;
            if (wday == target_wday) {
                result_day = day;
                break;
            }
        }
    } else if (w == week::last) {
        // Find the last occurrence
        for (int day = days_in_month; day >= 1; --day) {
            int wday = (first_day_wday + day - 1) % 7;
            if (wday == target_wday) {
                result_day = day;
                break;
            }
        }
    } else {
        // first, second, third, fourth
        int week_index = static_cast<int>(w); // 0, 1, 2, 3
        
        // Find the first occurrence
        int first_occurrence = -1;
        for (int day = 1; day <= 7; ++day) {
            int wday = (first_day_wday + day - 1) % 7;
            if (wday == target_wday) {
                first_occurrence = day;
                break;
            }
        }
        
        if (first_occurrence == -1) {
            throw std::invalid_argument("Weekday not found in first week");
        }
        
        result_day = first_occurrence + week_index * 7;
        
        if (result_day > days_in_month) {
            throw std::invalid_argument("Weekday not found in specified week");
        }
    }

    if (result_day == -1) {
        throw std::invalid_argument("Date not found");
    }

    return result_day;
}

}  // namespace meetup
