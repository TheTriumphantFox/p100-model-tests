#include "meetup.h"
#include <ctime>
#include <string>

namespace meetup {

// Helper function to calculate day of week for a given date
// Returns 0 for Sunday, 1 for Monday, ..., 6 for Saturday
int calculate_day_of_week(int year, unsigned int month, unsigned int day) {
    struct tm tm_struct = {};
    tm_struct.tm_year = year - 1900;
    tm_struct.tm_mon = month - 1;
    tm_struct.tm_mday = day;
    tm_struct.tm_hour = 12;
    tm_struct.tm_isdst = -1;
    
    time_t time = mktime(&tm_struct);
    struct tm* tm_result = localtime(&time);
    return tm_result->tm_wday;
}

// Helper function to get the number of days in a month
unsigned int get_days_in_month(int year, unsigned int month) {
    static const unsigned int days_in_month[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    unsigned int days = days_in_month[month - 1];
    // Check for leap year in February
    if (month == 2) {
        if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
            days = 29;
        }
    }
    return days;
}

meetup_date::meetup_date(int year, unsigned int month, unsigned int day)
    : year_(year), month_(month), day_(day) {}

int meetup_date::get_year() const {
    return year_;
}

unsigned int meetup_date::get_month() const {
    return month_;
}

unsigned int meetup_date::get_day() const {
    return day_;
}

meetup_date find_day(int year, unsigned int month, Week week, Day day) {
    unsigned int days_in_month = get_days_in_month(year, month);
    
    // Find all days in the month that match the requested weekday
    unsigned int matching_days[5]; // At most 5 occurrences of a weekday in a month
    int count = 0;
    
    for (unsigned int d = 1; d <= days_in_month; ++d) {
        int dow = calculate_day_of_week(year, month, d);
        if (dow == static_cast<int>(day)) {
            matching_days[count++] = d;
        }
    }
    
    unsigned int result_day = 0;
    
    switch (week) {
        case Week::teenth:
            // Find the day among 13-19 that matches the weekday
            for (unsigned int d = 13; d <= 19; ++d) {
                int dow = calculate_day_of_week(year, month, d);
                if (dow == static_cast<int>(day)) {
                    result_day = d;
                    break;
                }
            }
            break;
        case Week::first:
            result_day = matching_days[0];
            break;
        case Week::second:
            result_day = matching_days[1];
            break;
        case Week::third:
            result_day = matching_days[2];
            break;
        case Week::fourth:
            result_day = matching_days[3];
            break;
        case Week::last:
            result_day = matching_days[count - 1];
            break;
    }
    
    return meetup_date(year, month, result_day);
}

}  // namespace meetup
