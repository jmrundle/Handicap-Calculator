"""
database.py
"""
import sqlite3
import models
import os

# TODO: method to insert data -> decast from python object


DIR = "/Databases"

EXT = ".db"

COURSES_DB_NAME = "Courses"
HANDICAP_DB_NAME = "HandicapData"

COURSES_DB = os.path.join(DIR, COURSES_DB_NAME + EXT)
HANDICAP_DB = os.path.join(DIR, HANDICAP_DB_NAME + EXT)


class Connection:
    """
    Class with two main methods:
        write: used to insert information into the database (returns None)
        get: used to pull information from the database (returns a list)
    """
    def __init__(self, file_name):
        # check using working directory as reference
        if os.path.isfile(file_name):
            path = file_name

        # check using database directory as reference
        elif os.path.isfile(os.path.join(DIR, file_name)):
            path = os.path.join(DIR, file_name)

        # give up
        else:
            raise TypeError("File not found")

        self.file_name = file_name
        self.path = path
        self.conn = sqlite3.connect(path)

    @property
    def cursor(self):
        return self.conn.cursor()

    def write(self, query, params=None):
        """Writes information to a database via a SQL query"""
        if params is not None and isinstance(params, (tuple, list)):
            self.conn.execute(query, params)
        elif params is None:
            self.conn.execute(query)
        else:
            self.conn.execute(query, (params,))

        self.conn.commit()

    def get(self, query, params=None):
        """Gets an updated sqlite cursor object after a SQL query to the class database"""
        if params is not None and isinstance(params, (tuple, list)):
            return self.cursor.execute(query, params)
        elif params is None:
            return self.cursor.execute(query)
        else:
            return self.cursor.execute(query, (params,))

    def get_one(self, query, params=None):
        """Gets a single result from a SQL query to the class database"""
        return self.get(query, params).fetchone()

    def get_all(self, query, params=None):
        """Gets all results from a SQL query to the class database"""
        return self.get(query, params).fetchall()


"""
----------------------------------------------------------------------
Map sqlite query results to python object
----------------------------------------------------------------------
"""


class Mapping(Connection):
    def __init__(self, _class, db_path):
        """Maps a query result from a 'db_path' to a '_class' object"""
        # base database connection
        Connection.__init__(self, db_path)

        # first, map sqlite result to sqlite3.Row object
        # the mapped class must then take a sqlite3.Row object as its only input
        self.conn.row_factory = sqlite3.Row
        self._class = _class

    def get_one(self, *args, **kwargs):
        row = super().get_one(*args, **kwargs)
        return self._class(row)

    def get_all(self, *args, **kwargs):
        results = list()
        for row in super().get(*args, **kwargs):
            results.append(self._class(row))

        return results


# pre-made mappings to use upon import
courses = Mapping(models.Course, COURSES_DB)
tees = Mapping(models.Tee, COURSES_DB)
users = Mapping(models.User, HANDICAP_DB)
rounds = Mapping(models.Round, HANDICAP_DB)


def init_db():
    handicap_data = Connection(HANDICAP_DB)
    handicap_data.write("""
        CREATE TABLE IF NOT EXISTS "Users" ( 
        `UserID` INTEGER, 
        `Username` TEXT, 
        `Password` TEXT, 
        `Handicap` REAL, 
        `FirstName` TEXT, 
        `LastName` TEXT, 
        `Gender` TEXT, 
        PRIMARY KEY(`UserID`) ) 
        WITHOUT ROWID
        """)
    handicap_data.write("""
        CREATE TABLE IF NOT EXISTS "Rounds" ( 
        `RoundID` INTEGER, 
        `UserID` INTEGER, 
        `TeeID` INTEGER, 
        `Date` TEXT, 
        `Score` INTEGER, 
        `Differential` REAL, 
        `Type` TEXT, 
        PRIMARY KEY(`RoundID`) ) 
        WITHOUT ROWID
        """)


if __name__ == "__main__":
    init_db()
