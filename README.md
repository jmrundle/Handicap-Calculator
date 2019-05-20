# HandicapCalculator

A golf handicap is a number that represents a golfer's individual skill level, and it can be used for golfers of different skill levels to compete at an even playing field.  The Handicap Calculator uses an individual's scoring data and USGA difficulty ratings to calculate a user's golf handicap.


# Scripts
##### handicap.py
- Contains a variety of functions that manage the calculation of a handicap
- Supports both command line and GUI interfaces
##### distance.py
- Manages the calculation of distances between latitude and longitudinal values of courses
##### UserAPI.py
- Manages accounts and most database interactions
##### GUI.py
- Standard user interface for the handicap calculator program
- Incorporates a user login system
- Displays current handicap and 20 most recent scores
- Score entry involves a course search over a database with over 14,000 entries
- Provides ten course predictions for score entry based on current location and previous rounds
##### databases.py
- Simplifies interaction with each of the three databases

# Databases
##### Courses.db
- Contains the name, address, latitude, and longitude of every course in the U.S.
- Also stores the color, course rating, and slope rating of every tee for each course in the database
##### Users.db
- Contains information for user login
- Passwords are encrypted using the cryptography library
##### HandicapData.db
 - Contains scoring data for all rounds processed by the program, to be used for handicap calculation
