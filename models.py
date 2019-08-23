import distance
import handicap
import database as db
from accountManager import AccountManager

from datetime import datetime

manager = AccountManager()


class Tee:
    def __init__(self, row):
        self.id = row['TeeID']
        self.course_id = row['CourseID']
        self.color = row['Color']
        self.front_cr = row['FrontCR']
        self.front_sr = row['FrontSR']
        self.back_cr = row['BackCR']
        self.back_sr = row['BackSR']
        self.gender = row['Gender']

        # total cr is sum of each
        self.cr = round(self.front_cr + self.back_cr, 1)
        # total sr is rounded average of each
        # ex: 112.5 -> 113, 112.0 -> 112
        self.sr = int(round((self.front_sr + self.back_sr) / 2.0))


class Course:
    def __init__(self, row):
        self.id = row['CourseID']
        self.name = row['Name']
        self.state = row['State']
        self.city = row['City']
        self.address = row['Address']
        self.latitude = row['Latitude']
        self.longitude = row['Longitude']

        self.distance = distance.to((self.latitude, self.longitude))


class Round:
    def __init__(self, row):
        self.id = row['RoundID']
        self.score = row['Score']
        self.differential = row['Differential']
        self.type = row['Type']

        self.date = datetime.strptime(row['DateTime'], "%Y-%m-%dT%H:%M:%S")
        self.user = db.users.get_one("SELECT * FROM Users WHERE UserID = ?", row['UserID'])
        self.tee = db.tees.get_one("SELECT * FROM TeeData WHERE TeeID = ?", row['TeeID'])

        self.course = db.courses.get_one("SELECT * FROM CourseData WHERE CourseID = ?", self.tee.course_id)


class User:
    def __init__(self, row):
        self.id = row['UserID']
        self.username = row['Username']
        self.password = row['Password']
        self.first_name = row['FirstName']
        self.last_name = row['LastName']
        self.gender = row['Gender']

        self._handicap = handicap.format_handicap(row['Handicap'])

    def get_handicap(self):
        """Get's an updated version of a user's handicap"""
        self.update_handicap()
        return self._handicap

    def update_handicap(self):
        """Returns the updated version of the user's handicap"""
        rounds = manager.get_rounds(user=self, limit=20)

        # compile round tuples to list of differentials
        differentials = list(map(lambda r: r.differential, rounds))

        # calculate and properly format handicap index
        non_formatted_handicap = handicap.calculate_composite_handicap(differentials)
        self._handicap = handicap.format_handicap(non_formatted_handicap)

        # update database with new handicap index
        db.users.write("UPDATE Users SET Handicap = ? WHERE UserID = ?",
                       (non_formatted_handicap, self.id))
