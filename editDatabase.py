import sqlite3
import GoogleMaps

conn = sqlite3.connect("Databases/Courses.db")
cur = conn.cursor()

for id, name, state, city, address, lat, long in cur.execute("SELECT * FROM CourseData").fetchall():

    results = GoogleMaps.get_info(address=address, region=state)
    if results is not None:
        address = results[0]
        latitude = results[1][0]
        longitude = results[1][1]
        cur.execute("UPDATE CourseData SET address = ?, latitude = ?, longitude = ? WHERE id = ?",
                    (address, latitude, longitude, id))
        conn.commit()
    else:
        cur.execute("UPDATE CourseData SET address = 'N/A', latitude = 'N/A', longitude = 'N/A' WHERE id = ?", (id,))
        conn.commit()
        print("skipped one, id = " + str(id))

