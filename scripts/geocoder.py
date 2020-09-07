import requests
import sqlite3
import os


COURSES_DB = "/Applications/Programs/python/handicap_calculator/Databases/Courses.db"
conn = sqlite3.connect(COURSES_DB)


def get_geocode_data(course_name, city, state):
    cur = conn.cursor()
    cur.execute("SELECT Address, Latitude, Longitude FROM CourseData WHERE Name = {}".format(course_name))
    res = cur.fetchone()

    if res:
        return res
    else:
        params = {
            "address": f"{course_name}, {city}, {state}",
            "key": os.environ["GOOGLE_API_KEY"]
        }
        resp = requests.get(GOOGLE_GEOCODE_URL, params=params)
