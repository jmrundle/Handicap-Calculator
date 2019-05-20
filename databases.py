"""
databases.py
"""
import sqlite3


class Connection:
    """
    Class with two main methods:
        write: used to insert information into the database (returns None)
        get: used to pull information from the database (returns a list)
    """
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def write(self, query, params=None):
        """Writes information to a database via a SQL query"""
        if params is not None and isinstance(params, tuple):
            self.cursor.execute(query, params)
        elif params is None:
            self.cursor.execute(query)
        else:
            raise ValueError("Bad params argument")

        self.conn.commit()

    def get(self, query, params=None):
        """Gets an updated sqlite cursor object after a SQL query to the class database"""
        if params is not None and isinstance(params, tuple):
            return self.cursor.execute(query, params)
        elif params is None:
            return self.cursor.execute(query)
        else:
            raise ValueError("Bad params argument")

    def get_one(self, query, params=None):
        """Gets a single result from a SQL query to the class database"""
        return self.get(query, params).fetchone()

    def get_all(self, query, params):
        """Gets all results from a SQL query to the class database"""
        return self.get(query, params).fetchall()


users = Connection("Databases/Users.db")
users.write("""CREATE TABLE IF NOT EXISTS UserData(
                                            user_id INTEGER PRIMARY KEY,
                                            username TEXT,
                                            password TEXT,
                                            handicap REAL,
                                            first_name TEXT,
                                            last_name TEXT,
                                            gender TEXT)
                                            """)


rounds = Connection("Databases/HandicapData.db")
rounds.write("""CREATE TABLE IF NOT EXISTS Rounds(
                        round_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        course_id INTEGER,
                        course_name TEXT, 
                        date TEXT, 
                        tee_col TEXT,
                        cr TEXT,
                        sr TEXT,
                        score INTEGER, 
                        differential REAL,
                        type TEXT)""")

courses = Connection("Databases/Courses.db")
