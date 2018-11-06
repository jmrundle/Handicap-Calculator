import sqlite3
from cryptography.fernet import Fernet
from Handicap import Calculate


class AccountManager:

    def __init__(self, *args, **kwargs):
        self.account = None

        self.key = b'5n2-Wn3Zuutm6UcTLK_En1GRbdKx-cG7brrLgazsTbg='
        self.cipher_suite = Fernet(self.key)

        self.user_conn = sqlite3.connect("Databases/Users.db")
        self.user_cursor = self.user_conn.cursor()

        self.info_conn = sqlite3.connect("Databases/HandicapData.db")
        self.info_cursor = self.info_conn.cursor()

        self.user_cursor.execute("""CREATE TABLE IF NOT EXISTS UserData(
                                        user_id INTEGER PRIMARY KEY,
                                        username TEXT,
                                        password TEXT,
                                        handicap REAL,
                                        first_name TEXT,
                                        last_name TEXT,
                                        gender TEXT)
                                         """)
        self.user_conn.commit()

        self.info_cursor.execute("""CREATE TABLE IF NOT EXISTS Rounds(
                                round_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                course_id INTEGER,
                                course_name TEXT, 
                                date TEXT, 
                                tee_col TEXT,
                                cr_sr TEXT, 
                                score INTEGER, 
                                differential REAL,
                                type TEXT)""")
        self.info_conn.commit()

    def login(self, username, password):
        user = self.user_cursor.execute("SELECT * FROM UserData WHERE username=?", (username,))
        user = user.fetchone()
        if user:
            # get password associated with user; decrypt password; then compare to the given password
            # if the login was successful, the function will not raise any errors (will not return anything)
            if password != self.decrypt(user[2]):
                print(self.decrypt(user[2]))
                raise ValueError("Incorrect Password")
        else:
            raise ValueError("No user with the username '{}'.".format(username))
        self.account = Account(username)

    def log_out(self):
        self.account = None

    def change_password(self, username, new_password):
        self.user_cursor.execute("""UPDATE UserData
                                    SET password = ?
                                    WHERE username = ?
                                    """,
                                 (self.encrypt(new_password), username))
        self.user_conn.commit()

    def create_user(self, username, password, first, last, gender):
        # must be longer than 8 characters
        # must have at least one digit
        if len(password) < 8 or not any(map(lambda e: e.isdigit(), password)):
            raise ValueError("Password too weak")

        # search for username in UserData
        # if username already present, raise error
        check = self.user_cursor.execute("SELECT * FROM UserData WHERE username=?", (username,))
        if check.fetchone():
            raise ValueError("Username taken")

        # update UserInfo table with user data
        self.user_cursor.execute("""INSERT INTO UserData(username, password, first_name, last_name, gender)
                                 VALUES (?, ?, ?, ?, ?)""",
                                 (username, self.encrypt(password), first, last, gender))
        self.user_conn.commit()

    def delete_user(self, user_id):
        self.user_cursor.execute("DELETE FROM UserData WHERE user_id=?", (user_id,))
        self.user_conn.commit()

        self.info_cursor.execute("DELETE FROM Rounds WHERE user_id=?", (user_id,))
        self.info_conn.commit()

    def get_round_info(self, round_id):
        self.info_cursor.execute("SELECT * FROM Rounds WHERE round_id=?", (round_id,))
        return self.info_cursor.fetchone()

    def delete_round(self, round_id):
        self.info_cursor.execute("DELETE FROM Rounds WHERE round_id=?", (round_id,))
        self.info_conn.commit()

    def encrypt(self, text):
        # convert text from string into bytestring, then encrypt it
        return self.cipher_suite.encrypt(bytes(text).encode('utf-8'))

    def decrypt(self, text):
        bytestring = bytes(text).encode("utf-8")
        # convert encrypted bytestring into text bytestring
        unciphered_text = self.cipher_suite.decrypt(bytestring)
        # convert text bytestring into string, then return
        return bytes(unciphered_text).decode("utf-8")


class Account(AccountManager):

    def __init__(self, username):
        AccountManager.__init__(self)

        self.username = username

        self.user_id = self.get_info('user_id')
        self.first_name = self.get_info('first_name')
        self.last_name = self.get_info('last_name')
        self.gender = self.get_info('gender')

        # update handicap and assign it to variable
        self.update_index()

    def get_info(self, column):
        command = "SELECT {0} FROM UserData WHERE username='{1}'".format(column, self.username)
        return self.user_cursor.execute(command).fetchone()[0]

    def update_index(self):
        rounds = self.get_last_20()

        # compile tuples to a single list
        differentials = list(map(lambda r: r[8], rounds))

        # use Handicap.Calculate module to calculate handicap index
        not_formatted_handicap = Calculate.calculate_composite_handicap(differentials)
        self.handicap = Calculate.format_handicap(not_formatted_handicap)

        # update database with new handicap index
        self.user_cursor.execute("UPDATE UserData SET handicap = ? WHERE user_id = ?",
                                 (not_formatted_handicap, self.user_id))
        self.user_conn.commit()

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
            unpaired_round = self.info_cursor.execute("SELECT * FROM Rounds WHERE type = 'W'").fetchone()

            if unpaired_round:
                round_type = "C"
                unpaired_cr, unpaired_sr = unpaired_round[6].split('/')
                unpaired_name = unpaired_round[3]
                unpaired_score = unpaired_round[7]

                round_cr = round_cr + float(unpaired_cr)
                round_sr = (round_sr + int(unpaired_sr)) // 2
                round_sr = int(round_sr) + 1 if round_sr % 1 else int(round_sr)
                round_name = unpaired_name + " / " + course.name
                score += unpaired_score
                self.info_cursor.execute('DELETE FROM Rounds WHERE round_id = ?', (unpaired_round[0], ))

            # upload the 9 hole score, and wait for another nine hole score to pair it with
            else:
                round_type = "W"
                round_name = course.name

        differential = Calculate.calculate_round_handicap(score, round_cr, round_sr)
        self.info_cursor.execute("""INSERT INTO Rounds(user_id, course_id, course_name, date, tee_col, cr_sr, score, differential, type)
                                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (self.user_id, course.id, round_name, date, tee.color, '{}/{}'.format(round_cr, round_sr),
                                  score, differential, round_type)
                                 )
        self.info_conn.commit()
        self.update_index()

    def get_last_20(self):
        """Returns a list of user's 20 most recent handicap differentials from Scores database"""
        return self.info_cursor.execute("""SELECT * FROM Rounds
                                        WHERE user_id = ? AND
                                        type != 'W'
                                        ORDER BY date DESC
                                        LIMIT 20""",
                                        (self.user_id,)
                                        ).fetchall()
