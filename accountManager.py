import handicap
import distance
import models
import database as db

from cryptography.fernet import Fernet
from datetime import datetime
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

        key = os.environ.get('HANDICAP_KEY', None)
        if key is None:
            key = Fernet.generate_key()
            os.environ['HANDICAP_KEY'] = key

        self._cipher_suite = Fernet(encode(key))
    
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

        self._account = user

    def log_out(self):
        """Reset the internal account variable"""
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

    def upload_round_info(self, tee, score, date, holes_played='18', round_type="H", user=None):
        """Inputs user's data into Scores database"""
        # TODO: fix logic for 9 hole round pairings

        if user is None:
            user = self.get_account()

        if not isinstance(user, models.User):
            raise TypeError("Invalid 'user' parameter.  Must be of type Models.User.")

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
                                               user.id)

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
                        (user.id, tee.id, score, date, differential, round_type))

        user.update_handicap()

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

                round = self.get_round(round_id)
                cr = round.cr
                sr = round.sr
                h = handicap.calculate_round_handicap(score, cr, sr)

                db.rounds.write("UPDATE Rounds SET Score=?, Differential=? WHERE RoundID=?",
                                (score, h, round_id))
                round.user.update_handicap()

            except ValueError:
                return

    def get_rounds(self, user=None, limit=20):
        """Returns a list of user's 20 most recent handicap differentials from Scores database"""
        if user is None:
            user = self.get_account()

        if not isinstance(user, models.User):
            raise TypeError("Invalid 'user' parameter.  Must be of type Models.User.")

        return db.rounds.get_all("SELECT * FROM Rounds " +
                                 "WHERE UserID = ? AND Type != 'W' " +
                                 "ORDER BY DateTime DESC " +
                                 "LIMIT ?",
                                 (user.id, limit))

    def get_suggested_courses(self, user=None, limit=10):
        """Returns the course ids of 10 most relevant courses"""
        # relevant score
        #   decreases directly with distance
        #   decreases directly with days_since
        #   increases directly with times played
        #   = c1*timesPlayed / (c2*daysSince  * c3*distance)

        if user is None:
            user = self.get_account()

        if not isinstance(user, models.User):
            raise TypeError("Invalid 'user' parameter.  Must be of type Models.User.")

        today = datetime.today()
        recent_rounds = self.get_rounds(user=user, limit=30)
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

    @staticmethod
    def delete_round(round_id):
        """Delete a round from the database, then update that user's handicap"""
        round = db.rounds.get("SELECT * FROM Rounds WHERE RoundID = ?", round_id)

        db.rounds.write("DELETE FROM Rounds WHERE RoundID=?", round.id)

        round.user.update_handicap()

    @staticmethod
    def delete_user(user_id):
        """Delete a user and their rounds from the database"""
        db.users.write("DELETE FROM Users WHERE UserID=?", user_id)
        db.users.write("DELETE FROM Rounds WHERE UserID=?", user_id)

    @staticmethod
    def get_round(round_id):
        """Gets information about a given round in the database"""
        return db.rounds.get_one("SELECT * FROM Rounds WHERE RoundID=?", round_id)
