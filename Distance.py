import math                 # distance functions
import sqlite3              # accessing CourseData table
from geocoder import ip     # get latlong val of current location


current_pos = ip("me").latlng


def get_current_pos():
    return current_pos


def between(p1, p2):
    """Returns Euclidean distance in miles between two lat-long values"""
    # https://www.movable-type.co.uk/scripts/latlong.html
    try:
        radius = 3959.0  # miles
        x1 = math.radians(p1[0])
        x2 = math.radians(p2[0])
        dx = math.radians(p2[0] - p1[0])
        dy = math.radians(p2[1] - p1[1])
        
        a = math.sin(dx/2) * math.sin(dx/2) + \
            math.cos(x1) * math.cos(x2) * \
            math.sin(dy/2) * math.sin(dy/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return round(radius * c, 1)

    except TypeError:
        return -1


def within(max_dist, limit=20, from_pos=None):
    """Returns list of courses within a certain distance"""
    
    conn = sqlite3.connect("Databases/Courses.db")
    cur = conn.cursor()
    
    # if not given an initial position, set initial position to current location
    if from_pos is None:
        # if ip call doesn't work
        if current_pos is None:
            return []
        else:
            from_pos = current_pos
    
    ids = []
    for id, lat, long in cur.execute("SELECT id, latitude, longitude FROM CourseData").fetchall():
        try:
            to_pos = (float(lat), float(long))
            distance = between(from_pos, to_pos)
            if distance <= max_dist:
                ids.append((id, distance))
        except ValueError:
            # for courses without a latlong value ("N/A")
            pass

    # sort results by distance, and cut off by limit
    return sorted(ids, key=lambda x: x[1])[:limit]

