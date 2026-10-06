#if !defined(MEETUP_H)
#define MEETUP_H

#include <string>

namespace meetup {

enum class Week { first, second, third, fourth, teenth, last };
enum class Day { Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday };

class meetup_date {
public:
    meetup_date(int year, unsigned int month, unsigned int day);
    
    int get_year() const;
    unsigned int get_month() const;
    unsigned int get_day() const;
    
private:
    int year_;
    unsigned int month_;
    unsigned int day_;
};

meetup_date find_day(int year, unsigned int month, Week week, Day day);

}  // namespace meetup

#endif // MEETUP_H
