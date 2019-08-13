import handicap
from cryptography.fernet import Fernet
import distance
from datetime import datetime
import database as db
import os


def encode(string):
    if isinstance(string, str):
        return string.encode()
    return string


def decode(string):
    if isinstance(string, bytes):
        return string.decode()
    return string


class AccountManager:

    def __init__(self):
        self._account = None

        key = os.environ.get('HANDICAP_KEY').encode()
        if key is None:
            key_str = Fernet.generate_key()
            os.environ['HANDICAP_KEY'] = key_str
            key = key_str.encode()
        self._cipher_suite = Fernet(key)
    
    def _encrypt(self, text):
        """Encrypts password"""
        # convert text from string into bytestring, then encrypt it
        return self._cipher_suite.encrypt(encode(text))

    def _decrypt(self, text):
        """Decrypts password"""
        unciphered_text = self._cipher_suite.decrypt(encode(text))
        return decode(unciphered_text)

    def is_logged_in(self):
        return self._account is not None

    def get_account(self):
        if self.is_logged_in():
            return self._account
        raise ValueError("No account currently logged in")

    def login(self, username, password):
        """Checks to see if user/password combo is correct then updates global account variable"""
        user = db.users.get_one("SELECT * FROM Users WHERE Username=?", username)
        if user is not None:
            # get password associated with user; decrypt password; then compare to the given password
            # if the login was successful, the function will not raise any errors (will not return anything)
            if password != self._decrypt(user.password):
                raise ValueError("Incorrect Password")
        else:
            raise ValueError("No user with the username '{}'.".format(username))

        self._account = Account(user)

    def log_out(self):
        """Reset the global account variable"""
        self._account = None

    def change_password(self, username, new_password):
        """Changes a user's password"""
        db.users.write("UPDATE Users SET Password = ? WHERE Username = ?",
                       (self._encrypt(new_password), username))

    def create_user(self, username, password, first, last, gender):
        """Add a user to the database"""
        # search for username in Users
        # if username already present, raise error
        if db.users.get("SELECT UserID FROM Users WHERE Username=?", username):
            raise ValueError("Username taken")

        # must be longer than 8 characters
        # must have at least one digit and capital letter
        if len(password) < 8 or not any(map(lambda e: e.isdigit(), password)) or password == password.lower():
            raise ValueError("Password too weak")

        # update UserInfo table with user data
        db.users.write("INSERT INTO Users(Username, Password, First_name, Last_name, Gender) " +
                       "VALUES (?, ?, ?, ?, ?)",
                       (username, self._encrypt(password), first, last, gender))

    def delete_user(self, user_id):
        """Delete a user and their rounds from the database"""
        db.users.write("DELETE FROM Users WHERE UserID=?", user_id)
        db.users.write("DELETE FROM Rounds WHERE UserID=?", user_id)

    def get_round_info(self, round_id, column=None):
        """Gets information about a given round in the database"""
        if column is not None:
            results = db.rounds.get_one("SELECT {0} FROM Rounds " +
                                        "WHERE RoundID={1}""".format(column, round_id))
            return results[0] if results else None
        else:
            return db.rounds.get_one("SELECT * FROM Rounds WHERE RoundID=?", round_id)

    def update_round_info(self, round_id, date=None, score=None):
        """Update the date and/or score column of one of the user's rounds"""
        if date is not None:
            try:
                info = date.split("/")
                if len(info) != 3 \
                        or int(info[1]) > 12 or int(info[2]) > 31 \
                        or len(info[0]) + len(info[1]) + len(info[2]) != 8:
                    return

                db.rounds.write("UPDATE Rounds SET Date=? WHERE RoundID=?", (date, round_id))

            except (ValueError, AttributeError):
                return

        elif score is not None:
            try:
                if score < 18 or score > 999:
                    return
                cr = float(self.get_round_info(round_id, column="cr"))
                sr = float(self.get_round_info(round_id, column="sr"))

                h = handicap.calculate_round_handicap(score, cr, sr)
                db.rounds.write("UPDATE Rounds SET Score=?, Differential=? WHERE RoundID=?",
                               (score, h, round_id))
                self._account.update_handicap()

            except ValueError:
                return

    def upload_info(self, tee, score, date, holes_played='18', round_type="H"):
        """Inputs user's data into Scores database"""
        # TODO: fix logic for 9 hole round pairings

        if not self.is_logged_in():
            return ValueError("Account Not Logged In")

        if holes_played == '18':
            round_cr = tee.cr
            round_sr = tee.sr
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
            unpaired_round = db.rounds.get_one("SELECT * FROM Rounds WHERE Type = 'W' AND UserID = ?",
                                               self._account.id)

            if unpaired_round:
                round_type = "C"
                unpaired_cr = unpaired_round.tee.cr
                unpaired_sr = unpaired_round.tee.sr
                unpaired_score = unpaired_round.score

                round_cr = round_cr + float(unpaired_cr)
                round_sr = (round_sr + int(unpaired_sr)) // 2
                round_sr = int(round_sr) + 1 if round_sr % 1 else int(round_sr)
                score += unpaired_score
                db.rounds.write("DELETE FROM Rounds WHERE RoundID = ?", unpaired_round.round_id)

            # upload the 9 hole score, and wait for another nine hole score to pair it with
            else:
                round_type = "W"

        differential = handicap.calculate_round_handicap(score, round_cr, round_sr)
        db.rounds.write("INSERT INTO Rounds(UserID, TeeID, Score, DateTime, Differential, Type) " +
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (self._account.id, tee.id, score, date, differential, round_type))
        self._account.update_handicap()

    def get_rounds(self, limit=20):
        """Returns a list of user's 20 most recent handicap differentials from Scores database"""
        return db.rounds.get_all("SELECT * FROM Rounds " +
                                 "WHERE UserID = ? AND Type != 'W' " +
                                 "ORDER BY DateTime DESC " +
                                 "LIMIT ?",
                                 (self._account.id, limit))

    def delete_round(self, round_id):
        """Delete one of the user's rounds from the database"""
        db.rounds.write("DELETE FROM Rounds WHERE RoundID=?", round_id)
        self._account.update_handicap()

    def get_suggested_courses(self, limit=10):
        """Returns the course ids of 10 most relevant courses"""
        # relevant score
        #   decreases directly with distance
        #   decreases directly with days_since
        #   increases directly with times played
        #   = c1*timesPlayed / (c2*daysSince  * c3*distance)

        today = datetime.today()
        recent_rounds = self.get_rounds(limit=30)
        rounds = dict()  # contains popularity score of each course_id
        for i, round in enumerate(recent_rounds):

            days_since = (today - round.date).days

            if round.type == "C":
                # ignore combined scores (two courses)
                continue

            if round.course.id not in rounds:
                rounds[round.course.id] = 0.2 * (len(recent_rounds) - i)
            else:
                rounds[round.course.id] += 10 * (len(recent_rounds) - i)

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


# shortcut to access functionality
manager = AccountManager()


# --------------------------------------------- #
# -------------- ACCOUNT CLASS ---------------- #
# --------------------------------------------- #


class Account:
    def __init__(self, user, account_manager=manager):
        self.manager = account_manager

        # TODO: make Account class a child class of Models.User (or just make new model)
        self.id = user.id
        self.username = user.username
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.gender = user.gender

    @property
    def handicap(self):
        """The user's handicap"""
        return self.update_handicap()

    def update_handicap(self):
        """Returns the updated version of the user's handicap"""
        rounds = self.manager.get_rounds()

        # compile round tuples to list of differentials
        differentials = list(map(lambda r: r.differential, rounds))

        # calculate and properly format handicap index
        not_formatted_handicap = handicap.calculate_composite_handicap(differentials)
        formatted_handicap = handicap.format_handicap(not_formatted_handicap)

        # update database with new handicap index
        db.users.write("UPDATE Users SET Handicap = ? WHERE UserID = ?",
                       (not_formatted_handicap, self.id))

        return formatted_handicap

    def get_user_info(self):
        """Get information about the user"""
        return db.users.get_one("SELECT * FROM Users WHERE Username='{0}'".format(self.username))
