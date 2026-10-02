#if !defined(MEETUP_H)
#define MEETUP_H

#include <boost/date_time/gregorian/gregorian.hpp>
#include <string>

namespace meetup {

    class scheduler {
    public:
        scheduler(int year, int month) : year_(year), month_(month) {}

        boost::gregorian::date day(boost::date_time::weekdays weekday, std::string week) const {
            using namespace boost::gregorian;
            
            if (week == "first") {
                return find_nth_weekday(year_, month_, weekday, 1);
            } else if (week == "second") {
                return find_nth_weekday(year_, month_, weekday, 2);
            } else if (week == "third") {
                return find_nth_weekday(year_, month_, weekday, 3);
            } else if (week == "fourth") {
                return find_nth_weekday(year_, month_, weekday, 4);
            } else if (week == "last") {
                // Find the last occurrence of the weekday in the month
                // Start from the end of the month and go backwards
                date last_day = date(year_, month_ + 1, 1) - days(1);
                while (last_day.day_of_week() != weekday) {
                    last_day -= days(1);
                }
                return last_day;
            } else if (week == "teenth") {
                // Teenth days are 13-19
                for (int d = 13; d <= 19; ++d) {
                    date candidate(year_, month_, d);
                    if (candidate.day_of_week() == weekday) {
                        return candidate;
                    }
                }
            }
            
            // Default return (should rarely be reached)
            return date(year_, month_, 1);
        }

    private:
        int year_;
        int month_;
        
        // Helper to find the nth occurrence of a weekday in a month
        boost::gregorian::date find_nth_weekday(int year, int month, boost::date_time::weekdays weekday, int n) const {
             using namespace boost::gregorian;
             date d(year, month, 1);
             int count = 0;
             while (d.month() == month) {
                 if (d.day_of_week() == weekday) {
                     count++;
                     if (count == n) {
                         return d;
                     }
                 }
                 d += days(1);
             }
             // Return the first day of the month if not found (should rarely happen)
             return date(year, month, 1);
        }
    };

}  // namespace meetup

#endif // MEETUP_H
