import sqlite3


class Calculate:

    def __init__(self):
        self.conn = sqlite3.connect('Databases/Courses.db')
        self.cursor = self.conn.cursor()

        self.course = None
        self.tee = None

    def get_courses_from_name(self, course_name):
        """Queries search from course database then returns a list of course objects"""
        courses = []
        for course in self.cursor.execute("""SELECT * FROM CourseData WHERE
                                            name LIKE '%{0}%' LIMIT 25""".format(course_name)):
            courses.append(self.Course(*course))
        return courses

    def get_tees_from_course_id(self, id, gender=""):
        """Uses course's id to return a list of tee objects"""
        # by default, this method will not filter by gender
        # but, you can by changing the gender keyword arg to 'M' or 'F'
        tees = list()
        for tee in self.cursor.execute("""SELECT * FROM TeeData WHERE 
                                            course_id = {0} AND 
                                            gender LIKE '%{1}%'""".format(id, gender)).fetchall():
            tees.append(self.Tee(*tee[1:]))  # unpack everything except course_id
        return tees

    def set_course(self, course):
        self.course = course

    def set_tee(self, tee):
        self.tee = tee

    @staticmethod
    def calculate_round_handicap(score, cr, sr):
        return round((score - cr) * (113.0 / sr), 1)

    @staticmethod
    def calculate_composite_handicap(rounds):
        """Takes list of individual handicap values, and returns composite handicap as a float"""

        # USGA's table that determines how many rounds to use in calculation
        # key is number of available rounds
        # value is number of rounds to use in calculation
        number = len(rounds)
        if number < 5:
            return 0

        best = {
            5: 1, 6: 1, 7: 2, 8: 2, 9: 3, 10: 3, 11: 4, 12: 4,
            13: 5, 14: 5, 15: 6, 16: 6, 17: 7, 18: 8, 19: 9, 20: 10
        }[number]

        # take the first 'best' number of indexes
        usable = sorted(rounds)[:best]

        # average usable rounds, multiply by factor of 0.96, then truncate to 1 decimal point
        return float(format(0.96 * (sum(usable) / best), '.1f'))

    @staticmethod
    def format_handicap(num):
        """Formats handicap into a string"""
        try:
            return str(num) if num >= 0 else '+' + str(abs(num))
        except TypeError or ValueError:
            return num

    # Methods for use in a Python IDE

    @staticmethod
    def print_courses_table(courses):
        print()
        for i, course in enumerate(courses):
            print("{}. {} ({}, {})".format(i + 1, course.name, course.state, course.city))

    @staticmethod
    def print_tee_info(tees):
        men = True
        print("Men's:")

        for i, tee in enumerate(tees):
            # used to format men's tees under 'Men" header and women's tees under "Women" header
            if men and tee.gender == 'F':
                men = False
                print("Women's:")
            print("{}. {}: {} {}".format(i + 1, tee.color, tee.cr, tee.sr))

    # inner classes that contain tee and course info

    class Tee:
        def __init__(self, col, front_cr, front_sr, back_cr, back_sr, gender):
            self.color = col

            self.front_cr = float(front_cr)
            self.front_sr = int(front_sr)
            self.back_cr = float(back_cr)
            self.back_sr = int(back_sr)

            self.cr = round(self.front_cr + self.back_cr, 1)
            # rounds up if not an integer
            sr = (self.front_sr + self.back_sr) / 2
            self.sr = int(sr) if (sr % 1) == 0 else int(sr) + 1

            self.gender = gender


    class Course:
        def __init__(self, id, name, state, city):
            self.id = id
            self.name = name
            self.state = state
            self.city = city


if __name__ == '__main__':
    pass
    # jack = Calculate()
    # courses = jack.get_courses_from_name(input("Course Name (part or whole):\n>>> ").strip())
    # jack.print_courses_table(courses)
    # tees = jack.get_tees_from_course_id(courses[int(input("\nSelect Course. If not in menu, Enter 0.\n>>> ")) - 1].id)
    # jack.print_tee_info(tees)
    # tee = tees[int(input('\n>>> ')) - 1]
    # handicap = jack.calculate_round_handicap(int(input("\nScore:\n>>> ")), tee.cr, tee.sr)
    # print("\nHandicap is:", handicap)
