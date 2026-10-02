#if !defined(MEETUP_H)
#define MEETUP_H

#include <string>

namespace meetup {

    std::string day(std::string schedule, std::string weekday, int year, int month);

}  // namespace meetup

#endif // MEETUP_H
