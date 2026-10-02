#if !defined(MEETUP_H)
#define MEETUP_H

namespace meetup {

enum class week {
    first,
    second,
    third,
    fourth,
    last,
    teenth
};

enum class weekday {
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    sunday
};

class scheduler {
public:
    scheduler(int year, int month);
    int meetup(week w, weekday d);

private:
    int year_;
    int month_;
};

}  // namespace meetup

#endif // MEETUP_H
