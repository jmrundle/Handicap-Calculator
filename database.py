"""
database.py
"""
import sqlite3
import Models

# TODO: method to add -> decast from object


class Connection:
    """
    Class with two main methods:
        write: used to insert information into the database (returns None)
        get: used to pull information from the database (returns a list)
    """
    def __init__(self, path):
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
        Connection.__init__(self, db_path)
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


courses = Mapping(Models.Course, "Databases/Courses.db")
tees = Mapping(Models.Tee, "Databases/Courses.db")
users = Mapping(Models.User, "Databases/HandicapData.db")
rounds = Mapping(Models.Round, "Databases/HandicapData.db")


def init_db():
    handicap_data = Connection("Databases/Users.db")
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
