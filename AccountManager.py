import handicap
from cryptography.fernet import Fernet
import distance
from datetime import datetime
import databases
import os


account = None
key = os.environ.get('HANDICAP_KEY')
print key
cipher_suite = Fernet(key)


def encrypt(text):
    """Encrypts password"""
    # convert text from string into bytestring, then encrypt it
    return cipher_suite.encrypt(bytes(text).encode('utf-8'))


def decrypt(text):
    """Decrypts password"""
    bytestring = bytes(text).encode("utf-8")
    # convert encrypted bytestring into text bytestring
    unciphered_text = cipher_suite.decrypt(bytestring)
    # convert text bytestring into string, then return
    return bytes(unciphered_text).decode("utf-8")


def login(username, password):
    """Checks to see if user/password combo is correct then updates global account variable"""
    global account
    user = databases.users.get_one("""SELECT * 
                                      FROM UserData 
                                      WHERE username=?""",
                                   (username,))
    if user:
        # get password associated with user; decrypt password; then compare to the given password
        # if the login was successful, the function will not raise any errors (will not return anything)
        if password != decrypt(user[2]):
            print(decrypt(user[2]))
            raise ValueError("Incorrect Password")
    else:
        raise ValueError("No user with the username '{}'.".format(username))

    account = Account(username)
    return account


def log_out():
    """Reset the global account variable"""
    global account
    account = None


def change_password(username, new_password):
    """Changes a user's password"""
    databases.users.write("""UPDATE UserData
                             SET password = ?
                             WHERE username = ?""",
                          (encrypt(new_password), username))


def create_user(username, password, first, last, gender):
    """Add a user to the database"""
    # search for username in UserData
    # if username already present, raise error
    check = databases.users.get_one("""SELECT username 
                                       FROM UserData 
                                       WHERE username=?""",
                                    (username,))
    if check:
        raise ValueError("Username taken")

    # must be longer than 8 characters
    # must have at least one digit and capital letter
    if len(password) < 8 or not any(map(lambda e: e.isdigit(), password)) or password == password.lower():
        raise ValueError("Password too weak")

    # update UserInfo table with user data
    databases.users.write("""INSERT INTO UserData(username, password, first_name, last_name, gender)
                             VALUES (?, ?, ?, ?, ?)""",
                          (username, encrypt(password), first, last, gender))


def delete_user(user_id):
    """Delete a user and their rounds from the database"""
    databases.users.write("""DELETE FROM UserData 
                             WHERE user_id=?""",
                          (user_id,))

    databases.users.write("""DELETE FROM Rounds
                             WHERE user_id=?""",
                          (user_id,))


def get_round_info(round_id, column=None):
    """Gets information about a given round in the database"""
    if column is not None:
        results = databases.rounds.get_one("""SELECT {0} 
                                              FROM Rounds 
                                              WHERE round_id={1}""".format(column, round_id))
        return results[0] if results else None
    else:
        return databases.rounds.get_one("""SELECT * 
                                           FROM Rounds
                                           WHERE round_id=?""",
                                        (round_id, ))


# --------------------------------------------- #
# -------------- ACCOUNT CLASS ---------------- #
# --------------------------------------------- #


class Account:
    def __init__(self, username):
        self.username = username
        self.user_id = self.get_user_info('user_id')
        self.first_name = self.get_user_info('first_name')
        self.last_name = self.get_user_info('last_name')
        self.gender = self.get_user_info('gender')

    @property
    def handicap(self):
        """The user's handicap"""
        return self.update_handicap()

    def update_handicap(self):
        """Returns the updated version of the user's handicap"""
        rounds = self.get_rounds()

        # compile round tuples to list of differentials
        differentials = list(map(lambda r: r[-2], rounds))

        # calculate and properly format handicap index
        not_formatted_handicap = handicap.calculate_composite_handicap(differentials)
        formatted_handicap = handicap.format_handicap(not_formatted_handicap)

        # update database with new handicap index
        databases.users.write("""UPDATE UserData 
                                 SET handicap = ?
                                 WHERE user_id = ?""",
                              (not_formatted_handicap, self.user_id))

        return formatted_handicap

    def get_user_info(self, column):
        """Get information about the user"""
        assert column in ['user_id', 'username', 'password', 'handicap', 'first_name', 'last_name', 'gender']
        command = """SELECT {0}
                     FROM UserData
                     WHERE username='{1}'""".format(column, self.username)
        return databases.users.get_one(command)[0]
    
    def update_round_info(self, round_id, date=None, score=None):
        """Update the date and/or score column of one of the user's rounds"""
        if date is not None:
            try:
                info = date.split("/")
                if len(info) != 3\
                or int(info[1]) > 12 or int(info[2]) > 31\
                or len(info[0]) + len(info[1]) + len(info[2]) != 8:
                    return

                databases.rounds.write("""UPDATE Rounds
                                          SET date=?
                                          WHERE round_id=?""",
                                       (date, round_id))
        
            except (ValueError, AttributeError):
                return

        elif score is not None:
            try:
                if score < 18 or score > 999:
                    return
                cr = float(get_round_info(round_id, column="cr"))
                sr = float(get_round_info(round_id, column="sr"))
                
                h = handicap.calculate_round_handicap(score, cr, sr)
                databases.rounds.write("""UPDATE Rounds
                                          SET score=?, differential=?
                                          WHERE round_id=?""",
                                       (score, h, round_id))
                self.update_handicap()

            except ValueError:
                return

    def upload_info(self, course, tee, score, date, holes_played='18', round_type="H"):
        """Inputs user's data into Scores database"""
        if holes_played == '18':
            round_cr = tee.cr
            round_sr = tee.sr
            round_name = course.name
        else:
            if holes_played == '9F':
                round_cr = tee.front_cr
                round_sr = tee.front_sr
            elif holes_played == '9B':
                round_cr = tee.back_cr
                round_sr = tee.back_sr
            else:
                raise ValueError("Invalid holes_played param")

            # check if 9 hole round is waiting to be paired
            unpaired_round = databases.rounds.get_one("""SELECT * 
                                                         FROM Rounds
                                                         WHERE type = 'W'""")

            if unpaired_round:
                round_type = "C"
                unpaired_cr = unpaired_round[6]
                unpaired_sr = unpaired_round[7]
                unpaired_name = unpaired_round[3]
                unpaired_score = unpaired_round[8]

                round_cr = round_cr + float(unpaired_cr)
                round_sr = (round_sr + int(unpaired_sr)) // 2
                round_sr = int(round_sr) + 1 if round_sr % 1 else int(round_sr)
                if unpaired_name != course.name:
                    round_name = unpaired_name + " / " + course.name
                else:
                    round_name = course.name
                score += unpaired_score
                databases.rounds.write("""DELETE FROM Rounds
                                          WHERE round_id = ?""",
                                       (unpaired_round[0], ))

            # upload the 9 hole score, and wait for another nine hole score to pair it with
            else:
                round_type = "W"
                round_name = course.name

        differential = handicap.calculate_round_handicap(score, round_cr, round_sr)
        databases.rounds.write("""INSERT INTO Rounds(user_id, course_id, course_name, date, tee_col, cr, sr, score, differential, type)
                                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (self.user_id, course.id, round_name, date, tee.color,
                                  round_cr, round_sr, score, differential, round_type))
        self.update_handicap()

    def get_rounds(self, limit=20):
        """Returns a list of user's 20 most recent handicap differentials from Scores database"""
        return databases.rounds.get_all("""SELECT * FROM Rounds
                                           WHERE user_id = ? AND
                                                 type != 'W'
                                           ORDER BY date DESC, round_id DESC
                                           LIMIT ?""",
                                        (self.user_id, limit))

    def delete_round(self, round_id):
        """Delete one of the user's rounds from the database"""
        databases.rounds.write("""DELETE FROM Rounds
                                  WHERE round_id=?""",
                               (round_id,))
        self.update_handicap()

    def get_suggested_courses(self, limit=10):
        """Returns the course ids of 10 most relevant courses"""
        # relevant score
        #   decreases directly with distance
        #   decreases directly with days_since
        #   increases directly with times played
        #   = c1*timesPlayed / (c2*daysSince  * c3*distance)

        today = datetime.today()
        recent_rounds = self.get_rounds(limit=30)
        rounds = dict()     # contains popularity score of each course_id
        for i, round in enumerate(recent_rounds):
            course_id, date, type = round[2], round[4], round[9]

            y1, m1, d1 = map(int, date.split("/"))
            y2, m2, d2 = today.year, today.month, today.day
            days_since = 365 * (y2 - y1) + 30 * (m2 - m1) + d2 - d1

            if days_since < 1:
                days_since = 0.5

            if type == "C":
                # ignore combined scores (two courses)
                continue

            if course_id not in rounds:
                rounds[course_id] = 0.2 * (len(recent_rounds) - i) / days_since
            else:
                rounds[course_id] += 10 * (len(recent_rounds) - i) / days_since

        # involve courses near user in calculation
        near = distance.courses_within(30, limit=10)
        for course_id, dist in near:
            if course_id not in rounds:
                rounds[course_id] = 30 / dist
            else:
                rounds[course_id] *= 30 / dist

        # sort dict by relevant score, then convert to list of course_ids
        relevant_ids = list(map(lambda r: r[0], sorted(rounds.items(), key=lambda r: r[1], reverse=True)))

        return relevant_ids[:limit]
