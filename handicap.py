import distance
import databases

current_location = distance.current_pos


class Tee:
    def __init__(self, col, front_cr, front_sr, back_cr, back_sr, gender):
        self.color = col
        
        self.front_cr = float(front_cr)
        self.front_sr = int(front_sr)
        self.back_cr = float(back_cr)
        self.back_sr = int(back_sr)

        # total cr is sum of each
        self.cr = round(self.front_cr + self.back_cr, 1)
        # total sr is integer average of each
        # ex: 112.5 -> 113, 112.0 -> 112
        self.sr = int(round((self.front_sr + self.back_sr) / 2.0))
        
        self.gender = gender


class Course:
    def __init__(self, id, name, state, city, lat, long):
        self.id = id
        self.name = name
        self.state = state
        self.city = city
        self.distance = distance.between((lat, long), current_location)


def get_courses_from_name(course_name, limit=25):
    """Queries search from course database then returns a list of course objects"""
    courses = []

    for course in databases.courses.get_all("""SELECT id, name, state, city, latitude, longitude FROM CourseData WHERE
                                    name LIKE '%{0}%' LIMIT {1}""".format(course_name, limit)):
        courses.append(Course(*course))

    return sorted(courses, key=lambda c: c.distance)


def get_course_from_id(id):
    return Course(*databases.courses.get_one("""SELECT id, name, state, city, latitude, longitude 
                                                FROM CourseData 
                                                WHERE id = ?""", (id,)))


def get_tees_from_id(id, gender=""):
    """Uses course's id to return a list of tee objects"""
    # by default, this method will not filter by gender
    # but, you can by changing the gender keyword arg to 'M' or 'F'
    tees = list()
    for tee in databases.courses.get_all("""SELECT * 
                                            FROM TeeData 
                                            WHERE course_id = {0} 
                                            AND 
                                            gender LIKE '%{1}%'""".format(id, gender)):
        tees.append(Tee(*tee[1:]))  # unpack everything except course_id

    return tees


def calculate_round_handicap(score, cr, sr):
    return round((score - cr) * (113.0 / sr), 1)


def calculate_composite_handicap(rounds):
    """Takes list of individual handicap values, and returns composite handicap as a float"""
    
    # USGA's table that determines how many rounds to use in calculation
    # key is number of available rounds
    # value is number of rounds to use in calculation
    number = len(rounds)
    if number < 5:
        return "N/A"
    
    best = {
        5: 1, 6: 1, 7: 2, 8: 2, 9: 3, 10: 3, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 6, 16: 6, 17: 7, 18: 8, 19: 9, 20: 10
    }[number]

    # take the first 'best' number of indexes
    usable = sorted(rounds)[:best]
    
    # average usable rounds, multiply by factor of 0.96, then truncate to 1 decimal point
    return float(format(0.96 * (sum(usable) / best), '.1f'))


def format_handicap(num):
    """Formats handicap into a string"""
    try:
        return str(num) if num > -0.05 else '+' + str(abs(num))
    except (TypeError, ValueError):
        return num


# --------- Methods for output via command line --------- #


def print_courses_table(courses):
    print()
    for i, course in enumerate(courses):
        if isinstance(course, Course):
            print("{}. {} ({}, {})".format(i + 1, course.name, course.state, course.city))


def print_tee_info(tees):
    men = True
    print("Men's:")
    
    for i, tee in enumerate(tees):
        if isinstance(tee, Tee):
            # used to format men's tees under 'Men" header and women's tees under "Women" header
            if men and tee.gender == 'F':
                men = False
                print("Women's:")
            print("{}. {}: {} {}".format(i + 1, tee.color, tee.cr, tee.sr))
