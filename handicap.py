import database as db
import models


def get_courses_from_name(course_name, limit=25):
    query = "SELECT * FROM CourseData WHERE Name LIKE '%{0}%' LIMIT {1}".format(course_name, limit)

    courses = db.courses.get_all(query)

    return sorted(courses, key=lambda c: c.distance)


def get_course_from_id(course_id):
    query = "SELECT * FROM CourseData WHERE CourseID = ?"
    return db.courses.get_one(query, course_id)


def get_course_tees(course_id, gender=""):
    # by default, this method will not filter by gender
    # but, you can by changing the gender keyword arg to 'M' or 'F'
    query = "SELECT * FROM TeeData WHERE CourseID = {0} AND Gender LIKE '%{1}%'""".format(course_id, gender)
    return db.tees.get_all(query)


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
    if isinstance(num, str):
        return num
    if isinstance(num, int):
        return str(num) if num > -0.05 else '+' + str(abs(num))

    return TypeError("Invalid handicap argument")


# --------- Methods for output via command line --------- #


def print_courses_table(courses):
    print()
    for i, course in enumerate(courses):
        if isinstance(course, models.Course):
            print("{}. {} ({}, {})".format(i + 1, course.name, course.state, course.city))


def print_tee_info(tees):
    men = True
    print("Men's:")
    
    for i, tee in enumerate(tees):
        if isinstance(tee, models.Tee):
            # used to format men's tees under 'Men" header and women's tees under "Women" header
            if men and tee.gender == 'F':
                men = False
                print("Women's:")
            print("{}. {}: {} {}".format(i + 1, tee.color, tee.cr, tee.sr))
